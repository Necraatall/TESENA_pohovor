import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import Payment, PaymentCreate, PaymentPublic
from app.payment_service import (
    PaymentAlreadyPaidError,
    PaymentPendingError,
    create_payment,
)

router = APIRouter(tags=["payments"])


@router.post("/orders/{order_id}/payments", response_model=PaymentPublic)
def create_order_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    order_id: str,
    payment_in: PaymentCreate,
) -> Any:
    try:
        return create_payment(
            session=session,
            owner_id=current_user.id,
            order_id=order_id,
            payment_in=payment_in,
        )
    except (PaymentAlreadyPaidError, PaymentPendingError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/payments/{payment_id}", response_model=PaymentPublic)
def read_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    payment_id: uuid.UUID,
) -> Any:
    payment = session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if not current_user.is_superuser and payment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return payment
