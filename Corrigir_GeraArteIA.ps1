
$ErrorActionPreference = "Stop"

$Projeto = "W:\Projeto Pos\GeraArteIA"
$Python = Join-Path $Projeto ".venv\Scripts\python.exe"

Set-Location $Projeto

if (-not (Test-Path $Python)) {
    throw "Python do ambiente virtual não encontrado: $Python"
}

$Data = Get-Date -Format "yyyyMMdd_HHmmss"
$Backup = Join-Path $Projeto "backups\manutencao_$Data"
New-Item -ItemType Directory -Path $Backup -Force | Out-Null

$Arquivos = @(
    "web_app.py",
    "modal_app.py",
    "requirements.txt",
    ".gitignore",
    "app\generator.py",
    "app\prompt_optimizer.py",
    "app\database.py",
    "geraarteia.db"
)

foreach ($Arquivo in $Arquivos) {
    $Origem = Join-Path $Projeto $Arquivo

    if (Test-Path $Origem -PathType Leaf) {
        $Destino = Join-Path $Backup $Arquivo
        $PastaDestino = Split-Path $Destino -Parent

        New-Item -ItemType Directory -Path $PastaDestino -Force |
            Out-Null

        Copy-Item -LiteralPath $Origem -Destination $Destino -Force
    }
}

Write-Host ""
Write-Host "Backup criado em: $Backup" -ForegroundColor Green

$CodigoPython = @'
from pathlib import Path
import re
import sys

root = Path(r"W:\Projeto Pos\GeraArteIA")

def ler(caminho):
    return caminho.read_text(encoding="utf-8-sig")

def salvar(caminho, conteudo):
    caminho.write_text(conteudo, encoding="utf-8", newline="\n")

# 1. Ajusta as dependências para evitar Transformers 5.x,
# potencialmente incompatível com a versão do Diffusers utilizada.
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
        print("Dependências revisadas: transformers limitado à versão 4.x.")
    else:
        print("ATENÇÃO: requirements.txt está vazio; não foi reescrito.")

# 2. Garante que banco de dados e imagens geradas não sejam adicionados
# acidentalmente ao Git. Não apaga nem modifica esses arquivos.
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
    print(".gitignore já contém as regras de proteção.")

# 3. Ajusta o gerador para usar menos memória na GPU quando possível.
# Mantém uma alternativa para versões diferentes do Diffusers.
gerador = root / "app" / "generator.py"

if gerador.exists():
    conteudo = ler(gerador)

    if "enable_model_cpu_offload" in conteudo:
        print("Gerador já contém configuração de CPU offload.")
    else:
        # Só informa que a configuração precisa de análise manual
        # quando o trecho de carregamento não é reconhecido.
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
                print("Configuração de memória do gerador ajustada.")
            else:
                print("ATENÇÃO: gerador não foi alterado.")
        else:
            print(
                "ATENÇÃO: padrão de carregamento não reconhecido "
                "em app/generator.py; arquivo preservado."
            )

print("")
print("Etapa de manutenção concluída.")
print("Nenhum commit, push ou publicação foi executado.")
'@

$ArquivoPython = Join-Path $Backup "corrigir_projeto.py"
[System.IO.File]::WriteAllText(
    $ArquivoPython,
    $CodigoPython,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Aplicando ajustes com Python..." -ForegroundColor Cyan
& $Python $ArquivoPython

if ($LASTEXITCODE -ne 0) {
    throw "A etapa Python falhou. Backup preservado em: $Backup"
}

Write-Host ""
Write-Host "Validando sintaxe dos arquivos Python..." -ForegroundColor Cyan

& $Python -m compileall -q `
    (Join-Path $Projeto "app") `
    (Join-Path $Projeto "web_app.py") `
    (Join-Path $Projeto "modal_app.py")

if ($LASTEXITCODE -ne 0) {
    throw "Falha na compilação. Backup preservado em: $Backup"
}

Write-Host "Compilação concluída." -ForegroundColor Green

Write-Host ""
Write-Host "Executando testes..." -ForegroundColor Cyan

& $Python -m pytest -q

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Alguns testes falharam. Consulte as mensagens acima."
    Write-Warning "Backup preservado em: $Backup"
    exit 1
}

Write-Host ""
Write-Host "Manutenção e testes concluídos." -ForegroundColor Green
Write-Host "Backup: $Backup"
Write-Host "Nenhuma alteração foi enviada ao GitHub ou ao Modal."
