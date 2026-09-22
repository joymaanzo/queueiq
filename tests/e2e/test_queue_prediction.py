import subprocess

from playwright.sync_api import Page, expect


FRONTEND_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"


def open_app(page: Page) -> None:
    page.goto(FRONTEND_URL)
    expect(page.get_by_role("heading", name="Clinic wait-time made clearer.")).to_be_visible()


def test_frontend_and_health_endpoint(page: Page) -> None:
    open_app(page)
    response = page.request.get(f"{API_URL}/health")
    expect(response).to_be_ok()
    assert response.json()["status"] == "ok"


def test_select_clinic(page: Page) -> None:
    open_app(page)
    clinic_select = page.get_by_label("Clinic")
    expect(clinic_select).to_be_enabled()
    expect(clinic_select.locator("option")).to_have_count(4)
    clinic_select.select_option("2")
    expect(clinic_select).to_have_value("2")


def test_submit_prediction(page: Page) -> None:
    open_app(page)
    expect(page.get_by_label("Clinic")).to_be_enabled()
    page.get_by_label("Current queue length (optional)").fill("5")
    with page.expect_response(lambda response: response.url.endswith("/predict-wait-time") and response.request.method == "POST") as response_info:
        page.get_by_role("button", name="Predict wait time").click()
    response = response_info.value
    expect(response).to_be_ok()
    expect(page.get_by_text("minutes", exact=False).first).to_be_visible()


def test_prediction_persists_across_compose_restart(page: Page) -> None:
    open_app(page)
    page.get_by_label("Current queue length (optional)").fill("3")
    with page.expect_response(lambda response: response.url.endswith("/predict-wait-time") and response.request.method == "POST") as response_info:
        page.get_by_role("button", name="Predict wait time").click()
    prediction_id = response_info.value.json()["prediction_id"]

    before = subprocess.check_output(
        ["docker", "compose", "exec", "-T", "postgres", "psql", "-U", "queueiq", "-d", "queueiq", "-Atc", "SELECT count(*) FROM predictions"],
        text=True,
    ).strip()
    assert int(before) >= 1

    subprocess.run(["docker", "compose", "restart", "backend"], check=True)
    page.request.get(f"{API_URL}/health")
    after = subprocess.check_output(
        ["docker", "compose", "exec", "-T", "postgres", "psql", "-U", "queueiq", "-d", "queueiq", "-Atc", f"SELECT count(*) FROM predictions WHERE prediction_id = {int(prediction_id)}"],
        text=True,
    ).strip()
    assert after == "1"
