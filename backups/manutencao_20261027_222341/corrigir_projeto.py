from pathlib import Path
import re
import sys

root = Path(r"W:\Projeto Pos\GeraArteIA")

def ler(caminho):
    dados = caminho.read_bytes()
    if dados.startswith((b"\xff\xfe", b"\xfe\xff")):
        return dados.decode("utf-16")
    return dados.decode("utf-8-sig")

def salvar(caminho, conteudo):
    caminho.write_text(conteudo, encoding="utf-8", newline="\n")

# 1. Ajusta as dependÃªncias para evitar Transformers 5.x,
# potencialmente incompatÃ­vel com a versÃ£o do Diffusers utilizada.
req = root / "requirements.txt"

if req.exists():
    conteudo = ler(req)

    if conteudo.strip():
        linhas = []
        encontrou_transformers = False

        for linha in conteudo.splitlines():
            if re.match(r"^\s*transformers(?:\s|[<>=!~\[]|$)", linha, re.I):
                linhas.append("transformers>=4.41,<5.0")
                encontrou_transformers = True
            else:
                linhas.append(linha)

        if not encontrou_transformers:
            linhas.append("transformers>=4.41,<5.0")

        salvar(req, "\n".join(linhas) + "\n")
        print("DependÃªncias revisadas: transformers limitado Ã  versÃ£o 4.x.")
    else:
        print("ATENÃ‡ÃƒO: requirements.txt estÃ¡ vazio; nÃ£o foi reescrito.")

# 2. Garante que banco de dados e imagens geradas nÃ£o sejam adicionados
# acidentalmente ao Git. NÃ£o apaga nem modifica esses arquivos.
gitignore = root / ".gitignore"
conteudo_gitignore = ler(gitignore) if gitignore.exists() else ""

regras = [
    "",
    "# Dados locais e imagens geradas",
    "geraarteia.db",
    "geraarteia.db-*",
    "outputs/",
    "*.sqlite",
    "*.sqlite3",
]

novas = [
    regra for regra in regras
    if regra and regra not in conteudo_gitignore.splitlines()
]

if novas:
    conteudo_gitignore = conteudo_gitignore.rstrip() + "\n"
    conteudo_gitignore += "\n".join(novas) + "\n"
    salvar(gitignore, conteudo_gitignore)
    print(".gitignore atualizado para proteger dados locais.")
else:
    print(".gitignore jÃ¡ contÃ©m as regras de proteÃ§Ã£o.")

# 3. Ajusta o gerador para usar menos memÃ³ria na GPU quando possÃ­vel.
# MantÃ©m uma alternativa para versÃµes diferentes do Diffusers.
gerador = root / "app" / "generator.py"

if gerador.exists():
    conteudo = ler(gerador)

    if "enable_model_cpu_offload" in conteudo:
        print("Gerador jÃ¡ contÃ©m configuraÃ§Ã£o de CPU offload.")
    else:
        # SÃ³ informa que a configuraÃ§Ã£o precisa de anÃ¡lise manual
        # quando o trecho de carregamento nÃ£o Ã© reconhecido.
        padrao = r"pipe\.to\(DEVICE\)"

        if re.search(padrao, conteudo):
            substituto = """if DEVICE == "cuda":
            try:
                pipe.enable_model_cpu_offload()
            except Exception:
                pipe.to(DEVICE)
        else:
            pipe.to(DEVICE)"""

            conteudo_novo = re.sub(padrao, substituto, conteudo, count=1)

            if conteudo_novo != conteudo:
                salvar(gerador, conteudo_novo)
                print("ConfiguraÃ§Ã£o de memÃ³ria do gerador ajustada.")
            else:
                print("ATENÃ‡ÃƒO: gerador nÃ£o foi alterado.")
        else:
            print(
                "ATENÃ‡ÃƒO: padrÃ£o de carregamento nÃ£o reconhecido "
                "em app/generator.py; arquivo preservado."
            )

print("")
print("Etapa de manutenÃ§Ã£o concluÃ­da.")
print("Nenhum commit, push ou publicaÃ§Ã£o foi executado.")