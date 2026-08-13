from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import PaymentCreate, PaymentPublic
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
