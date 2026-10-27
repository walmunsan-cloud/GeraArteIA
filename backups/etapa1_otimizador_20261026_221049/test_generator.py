from app.prompt_optimizer import PromptOptimizer


def test_detectar_animal():
    optimizer = PromptOptimizer()

    categoria = optimizer.detectar_categoria(
        "Um cavalo correndo em um campo"
    )

    assert "animal" in categoria


def test_otimizar_animal():
    optimizer = PromptOptimizer()

    prompt = optimizer.otimizar(
        "Um cavalo marrom correndo"
    )

    assert "full body animal" in prompt
    assert "complete head and face" in prompt
