import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

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


def test_retry_after_failed_payment_creates_new_payment_attempt(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-RETRY-FAILED-{uuid.uuid4()}"

    failed_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "declined"},
    )
    retry_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert failed_response.status_code == 200
    assert retry_response.status_code == 200

    failed_payment = failed_response.json()
    retry_payment = retry_response.json()

    assert failed_payment["order_id"] == order_id
    assert retry_payment["order_id"] == order_id
    assert failed_payment["status"] == "FAILED"
    assert retry_payment["status"] == "PAID"

    assert failed_payment["payment_id"] != retry_payment["payment_id"]
    assert failed_payment["transaction_id"] != retry_payment["transaction_id"]
    assert (
        failed_payment["created_by_correlation_id"]
        != retry_payment["created_by_correlation_id"]
    )

    payments = db.exec(select(Payment).where(Payment.order_id == order_id)).all()

    assert len(payments) == 2
    assert {payment.status for payment in payments} == {
        PaymentStatus.FAILED,
        PaymentStatus.PAID,
    }


def test_retry_is_rejected_when_payment_is_pending(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-RETRY-PENDING-{uuid.uuid4()}"

    pending_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "timeout"},
    )
    retry_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert pending_response.status_code == 200
    assert pending_response.json()["status"] == "PENDING"

    assert retry_response.status_code == 409
    assert retry_response.json()["detail"] == "Order already has a pending payment"

    payments = db.exec(select(Payment).where(Payment.order_id == order_id)).all()

    assert len(payments) == 1
    assert payments[0].status == PaymentStatus.PENDING


def test_retry_is_rejected_when_payment_is_already_paid(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    order_id = f"QA-RETRY-PAID-{uuid.uuid4()}"

    paid_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "success"},
    )
    retry_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=normal_user_token_headers,
        json={"amount": 1250, "scenario": "declined"},
    )

    assert paid_response.status_code == 200
    assert paid_response.json()["status"] == "PAID"

    assert retry_response.status_code == 409
    assert retry_response.json()["detail"] == "Order is already paid"

    payments = db.exec(select(Payment).where(Payment.order_id == order_id)).all()

    assert len(payments) == 1
    assert payments[0].status == PaymentStatus.PAID
