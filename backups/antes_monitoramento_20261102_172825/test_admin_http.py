import ast
import base64
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SOURCE = Path(__file__).resolve().parents[1] / "modal_app.py"


class FakeStorage:
    def commit(self):
        return None


@pytest.fixture
def client(monkeypatch):
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    selected = []
    allowed_imports = {
        "json", "sqlite3", "shutil", "datetime", "pathlib", "uuid"
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
                target.id for target in node.targets
                if isinstance(target, ast.Name)
            ]
            if any(name in {
                "DATA_DIR", "OUTPUT_DIR", "BAD_DIR", "DB_PATH", "MODEL_ID"
            } for name in names):
                selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {
            "init_db", "fastapi_app"
        }:
            node.decorator_list = []
            selected.append(node)

    temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    root = Path(temp.name)

    namespace = {
        "__name__": "geraarteia_http_test",
        "storage": FakeStorage(),
    }

    exec(
        compile(ast.Module(body=selected, type_ignores=[]),
                str(SOURCE), "exec"),
        namespace,
    )

    namespace["DATA_DIR"] = root / "data"
    namespace["OUTPUT_DIR"] = root / "data" / "outputs"
    namespace["BAD_DIR"] = root / "data" / "revisao"
    namespace["DB_PATH"] = root / "data" / "geraarteia_test.db"

    monkeypatch.setenv("GERAARTEIA_ADMIN_USER", "admin")
    monkeypatch.setenv("GERAARTEIA_ADMIN_PASSWORD", "1234")

    app = namespace["fastapi_app"]()

    try:
        with TestClient(app) as test_client:
            yield test_client, app, namespace, root
    finally:
        # Fecha conexões SQLite mantidas em variáveis locais da aplicação,
        # caso existam, antes de remover o diretório temporário.
        for value in list(namespace.values()):
            if isinstance(value, object) and value.__class__.__name__ == "Connection":
                try:
                    value.close()
                except Exception:
                    pass
        temp.cleanup()


def auth(username="admin", password="1234"):
    token = base64.b64encode(
        f"{username}:{password}".encode("utf-8")
    ).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_health_publico(client):
    response = client[0].get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize("path", [
    "/admin",
    "/revisao",
    "/api/revisao",
    "/admin/testes/resultado",
    "/admin/testes/relatorio.txt",
    "/admin/testes/relatorio.pdf",
])
def test_rotas_admin_negam_acesso_sem_credenciais(client, path):
    response = client[0].get(path)
    assert response.status_code == 401


def test_senha_incorreta_e_rejeitada(client):
    response = client[0].get(
        "/admin", headers=auth(password="senha-errada")
    )
    assert response.status_code == 401


def test_admin_autenticado(client):
    response = client[0].get("/admin", headers=auth())
    assert response.status_code == 200
    assert "Administra" in response.text


def test_fila_de_revisao_autenticada(client):
    response = client[0].get("/api/revisao", headers=auth())
    assert response.status_code == 200
    assert response.json() == []


def test_relatorio_txt_autenticado(client):
    response = client[0].get(
        "/admin/testes/relatorio.txt", headers=auth()
    )
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "GeraArteIA" in response.text


def test_relatorio_pdf_autenticado(client):
    response = client[0].get(
        "/admin/testes/relatorio.pdf", headers=auth()
    )
    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert response.content.startswith(b"%PDF")


def test_imagem_de_revisao_nao_e_publica(client):
    response = client[0].get("/revisao/imagem/teste.png")
    assert response.status_code == 401


def test_endpoint_geracao_presente(client):
    app = client[1]
    routes = {
        (method, route.path)
        for route in app.routes
        for method in (getattr(route, "methods", None) or set())
    }
    assert ("POST", "/api/gerar") in routes

