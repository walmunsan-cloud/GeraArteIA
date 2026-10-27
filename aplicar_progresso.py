from pathlib import Path

generator_path = Path("app/generator.py")
web_path = Path("web_app.py")

generator = generator_path.read_text(encoding="utf-8")
web = web_path.read_text(encoding="utf-8")

old_signature = '''    def gerar(
        self,
        prompt: str,
        nome_arquivo: str = "imagem_gerada.png"
    ):'''

new_signature = '''    def gerar(
        self,
        prompt: str,
        nome_arquivo: str = "imagem_gerada.png",
        callback_progresso=None,
    ):'''

old_call = '''        resultado = self.pipe(
            prompt=prompt_final,
            negative_prompt=NEGATIVE_PROMPT,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            num_inference_steps=NUM_INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
        )'''

new_call = '''        def acompanhar_etapa(pipe, etapa, timestep, callback_kwargs):
            if callback_progresso is not None:
                percentual = int((etapa + 1) / NUM_INFERENCE_STEPS * 100)
                callback_progresso(
                    percentual,
                    etapa + 1,
                    NUM_INFERENCE_STEPS,
                )
            return callback_kwargs

        resultado = self.pipe(
            prompt=prompt_final,
            negative_prompt=NEGATIVE_PROMPT,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            num_inference_steps=NUM_INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
            callback_on_step_end=acompanhar_etapa,
        )'''

if old_signature not in generator:
    raise SystemExit("Não encontrei a assinatura esperada em app/generator.py. Nenhuma alteração foi feita nesse arquivo.")
if old_call not in generator:
    raise SystemExit("Não encontrei a chamada esperada do pipeline em app/generator.py. Nenhuma alteração foi feita nesse arquivo.")

generator = generator.replace(old_signature, new_signature, 1)
generator = generator.replace(old_call, new_call, 1)

old_globals = '''gerador = GeraArteIA(MODEL_PATH)
modelo_carregado = False'''

new_globals = '''gerador = GeraArteIA(MODEL_PATH)
modelo_carregado = False

progresso_geracao = {
    "ativo": False,
    "fase": "ocioso",
    "percentual": 0,
    "etapa": 0,
    "total_etapas": 0,
}'''

old_route_start = '''@app.post("/api/gerar")
def gerar_imagem(pedido: PedidoImagem):
    global modelo_carregado

    prompt = pedido.prompt.strip()'''

new_route_start = '''@app.get("/api/progresso")
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

    prompt = pedido.prompt.strip()'''

old_loading = '''    try:
        if not modelo_carregado:
            gerador.carregar_modelo()
            modelo_carregado = True

        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nome_arquivo = f"imagem_{data_hora}.png"

        caminho = gerador.gerar(
            prompt=prompt,
            nome_arquivo=nome_arquivo,
        )

        geracao_id = registrar_geracao(prompt, caminho.name)

        return {
            "sucesso": True,
            "id": geracao_id,
            "arquivo": caminho.name,
            "imagem": f"/api/imagem/{caminho.name}",
        }

    except HTTPException:
        raise
    except Exception as erro:
        print(f"Erro na geração: {erro}")
        raise HTTPException(
            status_code=500,
            detail=str(erro),
        )'''

new_loading = '''    progresso_geracao.update({
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
        )'''

if old_globals not in web:
    raise SystemExit("Não encontrei o bloco de inicialização em web_app.py.")
if old_route_start not in web:
    raise SystemExit("Não encontrei o início da rota de geração em web_app.py.")
if old_loading not in web:
    raise SystemExit("Não encontrei o corpo esperado da rota de geração em web_app.py.")

web = web.replace(old_globals, new_globals, 1)
web = web.replace(old_route_start, new_route_start, 1)
web = web.replace(old_loading, new_loading, 1)

generator_path.write_text(generator, encoding="utf-8")
web_path.write_text(web, encoding="utf-8")
print("Progresso real adicionado ao gerador e à API.")
