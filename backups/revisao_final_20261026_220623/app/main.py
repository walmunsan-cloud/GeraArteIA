from datetime import datetime
import os

from .generator import GeraArteIA


MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"


def abrir_imagem(caminho):
    """Abre a imagem gerada automaticamente no visualizador padrão do Windows."""
    try:
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

    gerador = GeraArteIA(MODEL_ID)

    try:
        gerador.carregar_modelo()
    except Exception as erro:
        print()
        print("Não foi possível carregar o modelo.")
        print(f"Erro: {erro}")
        return

    while True:

        print()
        print("=" * 55)
        print("              NOVA IMAGEM")
        print("=" * 55)
        print()
        print("O que você deseja gerar?")
        print()

        prompt = input("> ").strip()

        if not prompt:
            print()
            print("Digite uma descrição para gerar a imagem.")
            continue

        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")

        nome_arquivo = f"imagem_{data_hora}.png"

        try:

            caminho = gerador.gerar(
                prompt=prompt,
                nome_arquivo=nome_arquivo,
            )

            print()
            print("=" * 55)
            print("              IMAGEM PRONTA!")
            print("=" * 55)
            print()
            print(f"Arquivo: {caminho}")
            print()
            print("Abrindo imagem...")

            abrir_imagem(caminho)

            print()
            resposta = input("Deseja gerar outra imagem? (S/N): ").strip().lower()

            if resposta not in ["s", "sim"]:
                print()
                print("=" * 55)
                print("              GeraArteIA encerrado.")
                print("=" * 55)
                print()
                break

        except Exception as erro:

            print()
            print("=" * 55)
            print("             ERRO NA GERAÇÃO")
            print("=" * 55)
            print()
            print(f"Erro: {erro}")
            print()

            tentar = input("Deseja tentar novamente? (S/N): ").strip().lower()

            if tentar not in ["s", "sim"]:
                break


if __name__ == "__main__":
    main()