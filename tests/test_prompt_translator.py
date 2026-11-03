from app.prompt_translator import PromptTranslator


class FakeTokenizer:
    def __call__(self, textos, **kwargs):
        self.textos = textos
        return {"input_ids": [1]}

    def decode(self, resultado, **kwargs):
        return "A giraffe in the African savanna"


class FakeModel:
    def generate(self, **kwargs):
        return [[1]]


def test_tradutor_preserva_entrada_vazia():
    assert PromptTranslator.traduzir("   ") == ""


def test_tradutor_indica_portugues_e_retorna_ingles(monkeypatch):
    tokenizer = FakeTokenizer()

    monkeypatch.setattr(
        PromptTranslator, "_tokenizer", tokenizer
    )
    monkeypatch.setattr(
        PromptTranslator, "_model", FakeModel()
    )

    resultado = PromptTranslator.traduzir(
        "Uma girafa na savana africana"
    )

    assert tokenizer.textos == [
        ">>pt<< Uma girafa na savana africana"
    ]
    assert resultado == "A giraffe in the African savanna"


def test_tradutor_preserva_texto_original_se_saida_vazia(monkeypatch):
    class EmptyTokenizer(FakeTokenizer):
        def decode(self, resultado, **kwargs):
            return ""

    monkeypatch.setattr(
        PromptTranslator, "_tokenizer", EmptyTokenizer()
    )
    monkeypatch.setattr(
        PromptTranslator, "_model", FakeModel()
    )

    original = "Um SUV rosa com um laço rosa"
    assert PromptTranslator.traduzir(original) == original

def test_corrige_onca_pintada():
    resultado = PromptTranslator.corrigir_termos(
        "Uma onça-pintada realista para tatuagem.",
        "A realistic paint-once for tattooing",
    )
    assert "jaguar" in resultado.lower()
    assert "paint-once" not in resultado.lower()


def test_corrige_laco_rosa():
    resultado = PromptTranslator.corrigir_termos(
        "Um SUV rosa com um grande laço rosa.",
        "A pink SUV with a big pink loop",
    )
    assert "bow" in resultado.lower()
    assert "loop" not in resultado.lower()


def test_preserva_girafa_e_savana():
    resultado = PromptTranslator.corrigir_termos(
        "Uma girafa na savana africana.",
        "A giraffe in the African savannah",
    )
    assert "giraffe" in resultado.lower()
    assert "african savannah" in resultado.lower()
