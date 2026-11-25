from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics():
    client = TestClient(app)
    client.get("/health")
    client.get("/health/ready")
    client.get("/api/does-not-exist-for-metrics")
    response = client.get("/metrics")
    body = response.text

    assert response.status_code == 200
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert 'status="4xx"' in body  # 상태 코드는 2xx/4xx/5xx 로 묶임
    assert 'handler="/health"' not in body  # 헬스체크 프로브 제외
    assert 'handler="/health/ready"' not in body
    assert 'handler="/metrics"' not in body  # 수집 요청 자신도 제외
    assert client.get("/api/metrics").status_code == 404  # /api 프록시 경로로는 열리지 않음
    assert "/metrics" not in client.app.openapi()["paths"]  # API 문서에도 나오지 않음
