import uuid
from dataclasses import dataclass

from app.models import PaymentScenario


@dataclass(frozen=True)
class PaymentGatewayResult:
    transaction_id: uuid.UUID
    approved: bool
    failure_reason: str | None = None


class PaymentGatewayTimeoutError(Exception):
    def __init__(self, transaction_id: uuid.UUID) -> None:
        self.transaction_id = transaction_id
        super().__init__("Fake payment gateway timed out")


def process_payment(scenario: PaymentScenario) -> PaymentGatewayResult:
    transaction_id = uuid.uuid4()

    if scenario is PaymentScenario.SUCCESS:
        return PaymentGatewayResult(
            transaction_id=transaction_id,
            approved=True,
        )

    if scenario is PaymentScenario.DECLINED:
        return PaymentGatewayResult(
            transaction_id=transaction_id,
            approved=False,
            failure_reason="Payment declined",
        )

    if scenario is PaymentScenario.TIMEOUT:
        raise PaymentGatewayTimeoutError(transaction_id)

    raise ValueError(f"Unsupported payment scenario: {scenario}")
