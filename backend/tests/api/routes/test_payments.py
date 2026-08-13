import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Payment, PaymentStatus


def test_successful_payment_is_persisted_as_paid(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-SUCCESS-{uuid.uuid4()}"

    response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert response.status_code == 200
    payment_response = response.json()

    assert payment_response["order_id"] == order_id
    assert payment_response["status"] == "PAID"
    assert payment_response["failure_reason"] is None

    payment_id = uuid.UUID(payment_response["payment_id"])
    transaction_id = uuid.UUID(payment_response["transaction_id"])
    correlation_id = uuid.UUID(payment_response["created_by_correlation_id"])

    persisted_payment = db.get(Payment, payment_id)

    assert persisted_payment is not None
    assert persisted_payment.order_id == order_id
    assert persisted_payment.status == PaymentStatus.PAID
    assert persisted_payment.transaction_id == transaction_id
    assert persisted_payment.created_by_correlation_id == correlation_id


def test_declined_payment_is_persisted_as_failed(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-DECLINED-{uuid.uuid4()}"

    response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "declined"},
    )

    assert response.status_code == 200
    payment_response = response.json()

    assert payment_response["order_id"] == order_id
    assert payment_response["status"] == "FAILED"
    assert payment_response["failure_reason"] == "Payment declined"

    payment_id = uuid.UUID(payment_response["payment_id"])
    transaction_id = uuid.UUID(payment_response["transaction_id"])
    correlation_id = uuid.UUID(payment_response["created_by_correlation_id"])

    persisted_payment = db.get(Payment, payment_id)

    assert persisted_payment is not None
    assert persisted_payment.order_id == order_id
    assert persisted_payment.status == PaymentStatus.FAILED
    assert persisted_payment.transaction_id == transaction_id
    assert persisted_payment.created_by_correlation_id == correlation_id


def test_timeout_payment_is_persisted_as_pending(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-TIMEOUT-{uuid.uuid4()}"

    response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "timeout"},
    )

    assert response.status_code == 200
    payment_response = response.json()

    assert payment_response["order_id"] == order_id
    assert payment_response["status"] == "PENDING"
    assert payment_response["failure_reason"] == "Payment gateway timeout"

    payment_id = uuid.UUID(payment_response["payment_id"])
    transaction_id = uuid.UUID(payment_response["transaction_id"])
    correlation_id = uuid.UUID(payment_response["created_by_correlation_id"])

    persisted_payment = db.get(Payment, payment_id)

    assert persisted_payment is not None
    assert persisted_payment.order_id == order_id
    assert persisted_payment.status == PaymentStatus.PENDING
    assert persisted_payment.transaction_id == transaction_id
    assert persisted_payment.created_by_correlation_id == correlation_id
