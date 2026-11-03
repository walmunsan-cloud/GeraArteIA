from app.prompt_optimizer import PromptOptimizer


def test_detectar_animal():
    optimizer = PromptOptimizer()
    assert "animal" in optimizer.detectar_categoria(
        "Um cavalo correndo em um campo"
    )


def test_otimizar_animal():
    prompt = PromptOptimizer().otimizar("Um cavalo marrom correndo")
    assert "complete horse visible from head to hooves" in prompt
    assert "anatomically plausible equine proportions" in prompt
    assert "four visible hooves" in prompt
    assert "realistic animal photography" in prompt


def test_girafa_savana():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Uma girafa na savana")
    assert "complete giraffe visible from head to hooves" in prompt
    assert "long natural neck" in prompt
    assert "African savanna landscape" in prompt


def test_suv_rosa_laco():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Um SUV rosa com um laço rosa")
    assert "complete vehicle visible" in prompt
    assert "clearly visible decorative bow on the vehicle" in prompt
    assert "clearly pink vehicle paint" in prompt
    assert "realistic ribbon" in prompt


def test_onca_como_tatuagem():
    optimizer = PromptOptimizer()
    prompt = optimizer.otimizar("Uma tatuagem de onça-pintada")
    assert "professional jaguar tattoo design" in prompt
    assert "recognizable jaguar anatomy" in prompt
    assert "clean linework" in prompt
    assert "tattoo-ready artwork" in prompt


def test_ciclista_na_ciclovia():
    optimizer = PromptOptimizer()
    texto = "Um ciclista em uma ciclovia"
    prompt = optimizer.otimizar(texto)
    categoria = optimizer.detectar_categoria(texto)

    assert "pessoa" in categoria
    assert "veiculo" not in categoria
    assert "two visible wheels" in prompt
    assert "natural riding posture" in prompt
    assert "clearly defined bike lane" in prompt
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
    assert "professional jaguar tattoo design" in prompt
    assert "clean linework" in prompt


def test_otimizar_egua():
    prompt = PromptOptimizer().otimizar("Uma egua marrom em um campo")
    assert "complete horse visible from head to hooves" in prompt
    assert "four visible hooves" in prompt
    assert "natural mane and tail" in prompt


def test_otimizar_potro():
    prompt = PromptOptimizer().otimizar("Um potro correndo no pasto")
    assert "complete horse visible from head to hooves" in prompt
    assert "natural mane and tail" in prompt
    assert "entire horse inside the frame" in prompt