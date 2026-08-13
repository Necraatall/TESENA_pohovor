import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.models import Payment
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email


def test_create_payment_without_authentication_is_rejected(
    client: TestClient,
) -> None:
    order_id = f"QA-NO-AUTH-{uuid.uuid4()}"

    response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        json={"amount": 1250, "scenario": "success"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_user_cannot_read_another_users_payment(
    client: TestClient,
    db: Session,
) -> None:
    user_a_email = random_email()
    user_b_email = random_email()
    user_a_headers = authentication_token_from_email(
        client=client,
        email=user_a_email,
        db=db,
    )
    user_b_headers = authentication_token_from_email(
        client=client,
        email=user_b_email,
        db=db,
    )
    order_id = f"QA-AUTHZ-{uuid.uuid4()}"

    create_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=user_a_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert create_response.status_code == 200
    payment_id = create_response.json()["payment_id"]

    read_response = client.get(
        f"{settings.API_V1_STR}/payments/{payment_id}",
        headers=user_b_headers,
    )

    assert read_response.status_code == 403
    assert read_response.json() == {"detail": "Not enough permissions"}


def test_payment_state_of_another_user_does_not_affect_same_order_id(
    client: TestClient,
    db: Session,
) -> None:
    user_a_email = random_email()
    user_b_email = random_email()
    user_a_headers = authentication_token_from_email(
        client=client,
        email=user_a_email,
        db=db,
    )
    user_b_headers = authentication_token_from_email(
        client=client,
        email=user_b_email,
        db=db,
    )
    user_a = crud.get_user_by_email(session=db, email=user_a_email)
    user_b = crud.get_user_by_email(session=db, email=user_b_email)

    assert user_a is not None
    assert user_b is not None

    order_id = f"QA-OWNER-SCOPE-{uuid.uuid4()}"

    user_a_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=user_a_headers,
        json={"amount": 1250, "scenario": "success"},
    )
    user_b_response = client.post(
        f"{settings.API_V1_STR}/orders/{order_id}/payments",
        headers=user_b_headers,
        json={"amount": 1250, "scenario": "success"},
    )

    assert user_a_response.status_code == 200
    assert user_b_response.status_code == 200

    user_a_payment = user_a_response.json()
    user_b_payment = user_b_response.json()

    assert user_a_payment["order_id"] == order_id
    assert user_b_payment["order_id"] == order_id
    assert user_a_payment["status"] == "PAID"
    assert user_b_payment["status"] == "PAID"
    assert user_a_payment["owner_id"] == str(user_a.id)
    assert user_b_payment["owner_id"] == str(user_b.id)
    assert user_a_payment["owner_id"] != user_b_payment["owner_id"]
    assert user_a_payment["payment_id"] != user_b_payment["payment_id"]

    payments = db.exec(select(Payment).where(Payment.order_id == order_id)).all()

    assert len(payments) == 2
    assert {payment.owner_id for payment in payments} == {
        user_a.id,
        user_b.id,
    }
