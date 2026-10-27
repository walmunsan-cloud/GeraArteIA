from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import MODEL_PATH, OUTPUTS_DIR
from app.generator import GeraArteIA
from app.database import (
    registrar_geracao,
    avaliar_geracao,
    obter_estatisticas,
)


app = FastAPI(
    title="GeraArteIA",
    description="Sistema de geração de imagens por inteligência artificial.",
    version="1.1.0",
)

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


class PedidoImagem(BaseModel):
    prompt: str


class PedidoAvaliacao(BaseModel):
    geracao_id: int = Field(gt=0)
    nota: int = Field(ge=0, le=10)


gerador = GeraArteIA(MODEL_PATH)
modelo_carregado = False

progresso_geracao = {
    "ativo": False,
    "fase": "ocioso",
    "percentual": 0,
    "etapa": 0,
    "total_etapas": 0,
}


@app.get("/")
def inicio(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/api/status")
def status():
    return {
        "sistema": "GeraArteIA",
        "modelo": MODEL_PATH,
        "modelo_carregado": modelo_carregado,
    }


@app.get("/api/progresso")
def consultar_progresso():
    return dict(progresso_geracao)


@app.post("/api/gerar")
def gerar_imagem(pedido: PedidoImagem):
    global modelo_carregado

    if progresso_geracao["ativo"]:
        raise HTTPException(
            status_code=409,
            detail="Já existe uma geração em andamento. Aguarde a conclusão.",
        )

    prompt = pedido.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Digite uma descrição para gerar a imagem.",
        )

    progresso_geracao.update({
        "ativo": True,
        "fase": "carregando_modelo" if not modelo_carregado else "preparando",
        "percentual": 0,
        "etapa": 0,
        "total_etapas": 0,
    })

    try:
        if not modelo_carregado:
            gerador.carregar_modelo()
            modelo_carregado = True

        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nome_arquivo = f"imagem_{data_hora}.png"

        progresso_geracao["fase"] = "gerando"

        def atualizar_progresso(percentual, etapa, total):
            progresso_geracao.update({
                "ativo": True,
                "fase": "gerando",
                "percentual": percentual,
                "etapa": etapa,
                "total_etapas": total,
            })

        caminho = gerador.gerar(
            prompt=prompt,
            nome_arquivo=nome_arquivo,
            callback_progresso=atualizar_progresso,
        )

        geracao_id = registrar_geracao(prompt, caminho.name)

        progresso_geracao.update({
            "ativo": False,
            "fase": "concluido",
            "percentual": 100,
        })

        return {
            "sucesso": True,
            "id": geracao_id,
            "arquivo": caminho.name,
            "imagem": f"/api/imagem/{caminho.name}",
        }

    except HTTPException:
        progresso_geracao.update({"ativo": False, "fase": "erro"})
        raise
    except Exception as erro:
        progresso_geracao.update({"ativo": False, "fase": "erro"})
        print(f"Erro na geração: {erro}")
        raise HTTPException(
            status_code=500,
            detail=str(erro),
        )


@app.post("/api/avaliar")
def avaliar(pedido: PedidoAvaliacao):
    try:
        registrada = avaliar_geracao(pedido.geracao_id, pedido.nota)
        if not registrada:
            raise HTTPException(
                status_code=404,
                detail="Geração não encontrada.",
            )
        return {"sucesso": True, "estatisticas": obter_estatisticas()}
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(status_code=500, detail=str(erro))


@app.get("/api/dashboard")
def dashboard():
    return obter_estatisticas()


@app.get("/api/imagem/{nome_arquivo}")
def imagem(nome_arquivo: str):
    nome_seguro = Path(nome_arquivo).name
    caminho = OUTPUTS_DIR / nome_seguro

    if not caminho.is_file():
        raise HTTPException(
            status_code=404,
            detail="Imagem não encontrada.",
        )

    return FileResponse(
        path=caminho,
        media_type="image/png",
        filename=nome_seguro,
    )
