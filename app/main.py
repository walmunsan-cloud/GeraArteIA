from datetime import datetime
from pathlib import Path

from app.generator import GeraArteIA
from app.prompt_optimizer import PromptOptimizer
from app.config import OUTPUTS_DIR


def abrir_imagem(caminho):
    """Abre a imagem gerada no visualizador padrão do Windows."""
    try:
        import os
        os.startfile(str(caminho))
    except Exception as erro:
        print()
        print(f"Não foi possível abrir a imagem automaticamente: {erro}")


def main():
    print()
    print("=" * 55)
    print("                    GeraArteIA")
    print("=" * 55)
    print()
    print("Carregando inteligência artificial...")
    print()

    gerador = GeraArteIA()

    try:
        gerador.pipeline()
        print("Modelo carregado com sucesso.")
    except Exception as erro:
        print()
        print("Não foi possível carregar o modelo.")
        print(f"Erro: {erro}")
        return

    OUTPUTS_DIR_PATH = Path(OUTPUTS_DIR)
    OUTPUTS_DIR_PATH.mkdir(parents=True, exist_ok=True)

    while True:
        print()
        print("=" * 55)
        print("                  NOVA IMAGEM")
        print("=" * 55)
        print()
        print("O que você deseja gerar?")
        print()

        prompt = input("> ").strip()

        if not prompt:
            print()
            print("Digite uma descrição para gerar a imagem.")
            continue

        prompt_final = PromptOptimizer.otimizar(prompt)
        negativo = PromptOptimizer.prompt_negativo()

        print()
        print("Preparando descrição otimizada...")
        print("Gerando imagem...")

        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"imagem_{data_hora}.png"
        caminho = OUTPUTS_DIR_PATH / nome_arquivo

        try:
            imagem = gerador.generate(
                prompt=prompt_final,
                negative_prompt=negativo,
                steps=25,
                width=512,
                height=512,
            )

            imagem.save(caminho, format="PNG")

            print()
            print("=" * 55)
            print("                  IMAGEM PRONTA!")
            print("=" * 55)
            print()
            print(f"Prompt original: {prompt}")
            print(f"Arquivo: {caminho}")
            print()
            print("Abrindo imagem...")

            abrir_imagem(caminho)

            print()
            resposta = input(
                "Deseja gerar outra imagem? (S/N): "
            ).strip().lower()

            if resposta not in ("s", "sim"):
                print()
                print("GeraArteIA encerrado.")
                break

        except Exception as erro:
            print()
            print("=" * 55)
            print("                 ERRO NA GERAÇÃO")
            print("=" * 55)
            print()
            print(f"Erro: {erro}")
            print()

            tentar = input(
                "Deseja tentar novamente? (S/N): "
            ).strip().lower()

            if tentar not in ("s", "sim"):
                break


if __name__ == "__main__":
    main()