import uuid

from sqlmodel import Session, select

from app.models import Payment, PaymentCreate, PaymentStatus
from app.payment_gateway import PaymentGatewayTimeoutError, process_payment


class PaymentAlreadyPaidError(Exception):
    pass


class PaymentPendingError(Exception):
    pass


def create_payment(
    *,
    session: Session,
    owner_id: uuid.UUID,
    order_id: str,
    payment_in: PaymentCreate,
) -> Payment:
    statement = select(Payment.status).where(
        Payment.owner_id == owner_id,
        Payment.order_id == order_id,
    )
    existing_statuses = set(session.exec(statement).all())

    if PaymentStatus.PAID in existing_statuses:
        raise PaymentAlreadyPaidError("Order is already paid")

    if PaymentStatus.PENDING in existing_statuses:
        raise PaymentPendingError("Order already has a pending payment")

    correlation_id = uuid.uuid4()

    try:
        gateway_result = process_payment(payment_in.scenario)
    except PaymentGatewayTimeoutError as exc:
        payment = Payment(
            order_id=order_id,
            owner_id=owner_id,
            transaction_id=exc.transaction_id,
            created_by_correlation_id=correlation_id,
            amount=payment_in.amount,
            status=PaymentStatus.PENDING,
            failure_reason="Payment gateway timeout",
        )
    else:
        payment = Payment(
            order_id=order_id,
            owner_id=owner_id,
            transaction_id=gateway_result.transaction_id,
            created_by_correlation_id=correlation_id,
            amount=payment_in.amount,
            status=(
                PaymentStatus.PAID
                if gateway_result.approved
                else PaymentStatus.FAILED
            ),
            failure_reason=gateway_result.failure_reason,
        )

    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment
