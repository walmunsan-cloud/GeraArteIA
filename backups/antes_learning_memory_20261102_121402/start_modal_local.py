import ast
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_FILE = PROJECT_DIR / "modal_app.py"
DATA_DIR = PROJECT_DIR / "dados_local"
OUTPUT_DIR = DATA_DIR / "outputs"
BAD_DIR = DATA_DIR / "revisao"
DB_PATH = DATA_DIR / "geraarteia_local.db"


class LocalStorage:
    def commit(self):
        return None


def build_app():
    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {SOURCE_FILE}")

    tree = ast.parse(SOURCE_FILE.read_text(encoding="utf-8"))
    selected = []

    allowed_imports = {
        "json", "sqlite3", "shutil", "datetime", "pathlib", "uuid"
    }
    config_names = {
        "DATA_DIR", "OUTPUT_DIR", "BAD_DIR", "DB_PATH", "MODEL_ID"
    }

    for node in tree.body:
        if isinstance(node, ast.Import):
            if all(alias.name.split(".")[0] in allowed_imports
                   for alias in node.names):
                selected.append(node)

        elif isinstance(node, ast.ImportFrom):
            if node.module in allowed_imports:
                selected.append(node)

        elif isinstance(node, ast.Assign):
            names = [
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            ]
            if any(name in config_names for name in names):
                selected.append(node)

        elif isinstance(node, ast.FunctionDef) and node.name in {
            "init_db", "fastapi_app"
        }:
            node.decorator_list = []
            selected.append(node)

    namespace = {
        "__name__": "geraarteia_local_runtime",
        "storage": LocalStorage(),
    }

    code = compile(
        ast.Module(body=selected, type_ignores=[]),
        str(SOURCE_FILE),
        "exec",
    )
    exec(code, namespace)

    namespace.update({
        "DATA_DIR": DATA_DIR,
        "OUTPUT_DIR": OUTPUT_DIR,
        "BAD_DIR": BAD_DIR,
        "DB_PATH": DB_PATH,
    })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BAD_DIR.mkdir(parents=True, exist_ok=True)

    namespace["init_db"]()
    return namespace["fastapi_app"]()


if __name__ == "__main__":
    import uvicorn

    app = build_app()
    print("GeraArteIA - interface moderna em modo local")
    print(f"Dados locais: {DATA_DIR}")
    print("Endereço: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
