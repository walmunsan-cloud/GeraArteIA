from app.prompt_optimizer import PromptOptimizer


def test_detectar_animal():
    optimizer = PromptOptimizer()
    assert "animal" in optimizer.detectar_categoria(
        "Um cavalo correndo em um campo"
    )


def test_otimizar_animal():
    prompt = PromptOptimizer().otimizar("Um cavalo marrom correndo")
    assert "full body animal" in prompt
    assert "complete head and face" in prompt
    assert "anatomically plausible horse with four legs" in prompt
    assert "realistic galloping horse" in prompt


def test_girafa_savana():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Uma girafa na savana")
    assert "long natural giraffe neck" in prompt
    assert "savanna landscape" in prompt


def test_suv_rosa_laco():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Um SUV rosa com um laço rosa")
    assert "complete vehicle visible" in prompt
    assert "clearly visible bow accessory" in prompt
    assert "vehicle paint is pink" in prompt


def test_onca_como_tatuagem():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Uma tatuagem de onça-pintada")
    assert "tattoo design" in prompt
    assert "clean tattoo linework" in prompt


def test_ciclista_na_ciclovia():
    optimizer = PromptOptimizer()
    texto = "Um ciclista em uma ciclovia"
    prompt = optimizer.otimizar(texto)
    categoria = optimizer.detectar_categoria(texto)

    assert "pessoa" in categoria
    assert "veiculo" not in categoria
    assert "both wheels visible" in prompt
    assert "natural riding posture" in prompt
    assert "complete vehicle visible from front to rear" not in prompt


def test_prompt_vazio():
    assert PromptOptimizer().otimizar("   ") == ""


def test_acentos_nao_impedem_categoria():
    optimizer = PromptOptimizer()
    assert "animal" in optimizer.detectar_categoria("Uma girafa na savana")


def test_tatuagem_onca_adiciona_instrucoes():
    optimizer = PromptOptimizer()
    texto = "Uma tatuagem realista de uma onça"
    prompt = optimizer.otimizar(texto)
    assert "tattoo design" in prompt
    assert "clean tattoo linework" in prompt
