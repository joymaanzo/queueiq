from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_clinics():
    response = client.get("/clinics")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_predict_unconditional():
    response = client.post(
        "/predict-wait-time",
        json={"clinic_id": 1, "timestamp": "2026-09-11T09:00:00"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "unconditional"
    assert body["prediction_id"] > 0


def test_predict_conditional():
    response = client.post(
        "/predict-wait-time",
        json={
            "clinic_id": 1,
            "timestamp": "2026-09-11T09:00:00",
            "current_queue_length": 5,
        },
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "conditional"


def test_predict_invalid_clinic_404():
    response = client.post(
        "/predict-wait-time",
        json={"clinic_id": 999, "timestamp": "2026-09-11T09:00:00"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "CLINIC_NOT_FOUND"


def test_predict_invalid_queue_400():
    response = client.post(
        "/predict-wait-time",
        json={
            "clinic_id": 1,
            "timestamp": "2026-09-11T09:00:00",
            "current_queue_length": 101,
        },
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_QUEUE_LENGTH"


def test_record_actual_success():
    prediction = client.post(
        "/predict-wait-time",
        json={"clinic_id": 1, "timestamp": "2026-09-11T09:00:00", "current_queue_length": 5},
    ).json()
    response = client.post(
        "/record-actual-wait",
        json={"prediction_id": prediction["prediction_id"], "actual_wait_minutes": 12.0},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
    assert response.json()["error_minutes"] == prediction["predicted_wait_minutes"] - 12.0


def test_record_actual_duplicate_409():
    prediction = client.post(
        "/predict-wait-time",
        json={"clinic_id": 1, "timestamp": "2026-09-11T09:00:00", "current_queue_length": 5},
    ).json()
    payload = {"prediction_id": prediction["prediction_id"], "actual_wait_minutes": 12.0}
    client.post("/record-actual-wait", json=payload)
    response = client.post("/record-actual-wait", json=payload)
    assert response.status_code == 409
    assert response.json()["code"] == "ACTUAL_WAIT_ALREADY_REPORTED"


def test_record_actual_invalid_prediction_404():
    response = client.post(
        "/record-actual-wait",
        json={"prediction_id": 999999999, "actual_wait_minutes": 12.0},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "PREDICTION_NOT_FOUND"


def test_stats_endpoint():
    response = client.get("/clinic/1/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["clinic_id"] == 1
    assert body["hourly_stats"]
    assert body["daily_stats"]


def test_forecast_endpoint():
    response = client.get("/clinic/1/forecast")
    assert response.status_code == 200
    forecast = response.json()["forecast"]
    assert len(forecast) == 3
    assert [entry["hours_ahead"] for entry in forecast] == [1, 2, 4]


def test_evaluation_endpoint():
    response = client.get("/clinic/1/evaluation")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "clinic_id",
        "predictions_with_actuals",
        "model_mae",
        "baseline_mae",
        "improvement_pct",
        "interval_coverage",
        "interval_level",
        "events_evaluated",
    }
    assert body["clinic_id"] == 1
    assert body["events_evaluated"] <= 50
    assert 0.0 <= body["interval_coverage"] <= 1.0
    assert body["interval_level"] == 0.8


def test_evaluation_clinic_not_found():
    response = client.get("/clinic/999/evaluation")
    assert response.status_code == 404
    assert response.json()["code"] == "CLINIC_NOT_FOUND"
