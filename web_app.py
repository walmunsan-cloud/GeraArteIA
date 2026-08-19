from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import MODEL_PATH, OUTPUTS_DIR
from app.generator import GeraArteIA


app = FastAPI(
    title="GeraArteIA",
    description="Sistema de geração de imagens por inteligência artificial.",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static",
)


templates = Jinja2Templates(
    directory="web/templates"
)


class PedidoImagem(BaseModel):
    prompt: str


gerador = GeraArteIA(MODEL_PATH)

modelo_carregado = False


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


@app.post("/api/gerar")
def gerar_imagem(pedido: PedidoImagem):

    global modelo_carregado

    prompt = pedido.prompt.strip()

    if not prompt:

        raise HTTPException(
            status_code=400,
            detail="Digite uma descrição para gerar a imagem.",
        )

    try:

        if not modelo_carregado:

            gerador.carregar_modelo()

            modelo_carregado = True

        data_hora = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        nome_arquivo = f"imagem_{data_hora}.png"

        caminho = gerador.gerar(
            prompt=prompt,
            nome_arquivo=nome_arquivo,
        )

        return {
            "sucesso": True,
            "arquivo": caminho.name,
            "imagem": f"/api/imagem/{caminho.name}",
        }

    except Exception as erro:

        print(f"Erro na geração: {erro}")

        raise HTTPException(
            status_code=500,
            detail=str(erro),
        )


@app.get("/api/imagem/{nome_arquivo}")
def imagem(nome_arquivo: str):

    caminho = OUTPUTS_DIR / nome_arquivo

    if not caminho.exists():

        raise HTTPException(
            status_code=404,
            detail="Imagem não encontrada.",
        )

    return FileResponse(
        path=caminho,
        media_type="image/png",
        filename=nome_arquivo,
    )