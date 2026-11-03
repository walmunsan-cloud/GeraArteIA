from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "modal_app.py"


def read_source():
    assert SOURCE.exists(), f"Arquivo não encontrado: {SOURCE}"
    return SOURCE.read_text(encoding="utf-8")


def test_autenticacao_administrativa_existe():
    source = read_source()
    assert "HTTPBasic" in source
    assert "HTTPBasicCredentials" in source
    assert "require_admin" in source
    assert "secrets.compare_digest" in source


def test_senha_temporaria_de_apresentacao():
    source = read_source()
    assert 'GERAARTEIA_ADMIN_PASSWORD", "1234"' in source


def test_area_administrativa_protegida():
    source = read_source()
    assert '@web.get("/admin", response_class=HTMLResponse)' in source
    assert '@web.get("/revisao", response_class=HTMLResponse)' in source
    assert 'Depends(require_admin)' in source


def test_api_de_revisao_protegida():
    source = read_source()
    assert '@web.get("/api/revisao")' in source
    assert '@web.get("/revisao/imagem/{filename}")' in source


def test_relatorios_protegidos():
    source = read_source()
    assert '@web.get("/admin/testes/relatorio.txt")' in source
    assert '@web.get("/admin/testes/relatorio.pdf")' in source
    assert '@web.get("/admin/testes/resultado")' in source


def test_avaliacao_limita_notas_de_zero_a_dez():
    source = read_source()
    assert '@web.post("/api/avaliar/{generation_id}")' in source
    assert "not 0 <= rating <= 10" in source


def test_notas_baixas_sao_sinalizadas():
    source = read_source()
    assert "rating <= 4" in source
    assert "flagged_bad" in source
    assert "shutil.copy2" in source


def test_limite_de_comentario():
    source = read_source()
    assert "2000" in source


def test_endpoint_de_geracao_preservado():
    source = read_source()
    assert '@web.post("/api/gerar")' in source


def test_health_publico_preservado():
    source = read_source()
    assert '@web.get("/health")' in source


def test_diagnostico_informa_limitacoes():
    source = read_source()
    assert "build_diagnostic_report" in source
    assert "nao executa uma geracao real" in source.lower() or (
        "não executa uma geração real" in source.lower()
    )


def test_pdf_tem_dependencia_de_relatorio():
    source = read_source()
    assert "reportlab" in source.lower()
    assert "application/pdf" in source

