import modal

app = modal.App("geraarteia-teste-tradutor")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers>=4.41,<5",
        "sentencepiece>=0.2.0",
    )
)

@app.function(
    image=image,
    timeout=900,
    cpu=2,
    memory=4096,
)
def testar_tradutor():
    import torch
    from transformers import MarianMTModel, MarianTokenizer

    model_id = "Helsinki-NLP/opus-mt-ROMANCE-en"

    print("\nCarregando tradutor MarianMT...")
    tokenizer = MarianTokenizer.from_pretrained(model_id)
    model = MarianMTModel.from_pretrained(model_id)
    model.to("cpu")
    model.eval()

    frases = [
        "Uma girafa na savana africana.",
        "Um SUV rosa com um grande laço rosa.",
        "Uma onça-pintada realista para tatuagem.",
    ]

    print("\n=== RESULTADOS DA TRADUCAO ===")

    for frase in frases:
        entrada = tokenizer(
            [">>pt<< " + frase],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        with torch.inference_mode():
            resultado = model.generate(
                **entrada,
                max_new_tokens=512,
                num_beams=4,
            )

        traducao = tokenizer.decode(
            resultado[0],
            skip_special_tokens=True,
        )

        print("\nPORTUGUES:", frase)
        print("INGLES:", traducao)

    return "TESTE_CONCLUIDO"


@app.local_entrypoint()
def main():
    resultado = testar_tradutor.remote()
    print("\nRESULTADO FINAL:", resultado)
