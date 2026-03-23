from unittest.mock import patch

from app.domain.models import AnalysisResult

MOCK_RESULT = AnalysisResult(
    score=80,
    level="Pleno",
    strong_points=["Forte domínio de Python", "Portfólio de projetos consistente"],
    weak_points=["Sem experiência formal em liderança"],
    suggestions=["Obter certificação em nuvem", "Contribuir com projetos de código aberto"],
    detected_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs"],
)

FAKE_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "versao" in data


def test_analisar_sem_arquivo(client):
    response = client.post("/analyze")
    assert response.status_code == 422


def test_analisar_tipo_invalido(client):
    response = client.post(
        "/analyze",
        files={"file": ("curriculo.txt", b"conteudo em texto simples", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@patch("app.api.routes.analyze.analyzer")
@patch("app.api.routes.analyze.pdf_extractor")
def test_analisar_pdf_sucesso(mock_extractor, mock_analyzer, client):
    mock_extractor.extract_text.return_value = "Maria Silva - Engenheira de Software Sênior"
    mock_analyzer.analyze.return_value = MOCK_RESULT

    response = client.post(
        "/analyze",
        files={"file": ("curriculo.pdf", FAKE_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["score"] == 80
    assert data["level"] == "Pleno"
    assert isinstance(data["strong_points"], list)
    assert isinstance(data["weak_points"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["detected_skills"], list)
    assert data["filename"] == "curriculo.pdf"
    assert "id" in data
    assert "created_at" in data


def test_historico_retorna_paginado(client):
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


def test_historico_parametros_paginacao(client):
    response = client.get("/history?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5


def test_historico_nao_encontrado(client):
    response = client.get("/history/999999")
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]


@patch("app.api.routes.analyze.analyzer")
@patch("app.api.routes.analyze.pdf_extractor")
def test_historico_apos_analise(mock_extractor, mock_analyzer, client):
    mock_extractor.extract_text.return_value = "João Costa - Desenvolvedor Backend"
    mock_analyzer.analyze.return_value = MOCK_RESULT

    client.post(
        "/analyze",
        files={"file": ("curriculo_teste.pdf", FAKE_PDF, "application/pdf")},
    )

    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert "score" in data["items"][0]
    assert "level" in data["items"][0]
    assert "filename" in data["items"][0]
