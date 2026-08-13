import uuid

from fastapi.testclient import TestClient

from app.core.config import settings


def test_payment_with_zero_amount_is_rejected(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    order_id = f"QA-ZERO-AMOUNT-{uuid.uuid4()}"

    response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 0, "scenario": "success"},
    )

    assert response.status_code == 422


def test_get_existing_payment_returns_created_payment(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    order_id = f"QA-GET-PAYMENT-{uuid.uuid4()}"

    create_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert create_response.status_code == 200
    created_payment = create_response.json()

    read_response = client.get(
        f"{settings.API_V1_STR}/payments/{created_payment['payment_id']}",
        headers=normal_user_token_headers,
    )

    assert read_response.status_code == 200
    read_payment = read_response.json()

    assert read_payment == created_payment


def test_get_unknown_payment_returns_not_found(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    unknown_payment_id = uuid.uuid4()

    response = client.get(
        f"{settings.API_V1_STR}/payments/{unknown_payment_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Payment not found"}
