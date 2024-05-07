import logging
from decimal import Decimal
from typing import Optional

from .allocation import Allocation
from .types import BankClient


def _check_minimum_amount(
    amount: Decimal, *, minimum_amount: Optional[Decimal]
) -> Decimal:
    if amount > (minimum_amount if minimum_amount else 0):
        return amount
    else:
        logging.info(
            f"\t Amount {amount} is less than minimum amount {minimum_amount}. Skipping."
        )
        return Decimal(0)


def _check_maximum_amount(
    amount: Decimal, *, maximum_amount: Optional[Decimal]
) -> Decimal:
    if maximum_amount is not None and amount > maximum_amount:
        logging.info(
            f"\t Amount {amount} exceeds maximum amount {maximum_amount}. Using maximum amount."
        )
        return maximum_amount
    else:
        return amount


def _check_remainder(amount: Decimal, *, remainder: Decimal) -> Decimal:
    if amount < remainder:
        return amount
    else:
        logging.info(
            f"\t Amount {amount} exceeds remainder {remainder}. Using remainder."
        )
        return remainder


def top_up_strategy(
    allocation: Allocation, remainder: Decimal, *, bank_client: BankClient
) -> Decimal:
    logging.info(
        f"Attempting to top up allocation {allocation.description} to {allocation.value}."
    )
    balance = bank_client.get_balance_by_iban(iban=allocation.target_iban)
    amount = allocation.value - balance
    if amount < 0:
        logging.info(f"\t Skipping allocation. Balance is already sufficient.")
        return Decimal(0)

    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


def fixed_strategy(allocation: Allocation, remainder: Decimal, *_, **__) -> Decimal:
    logging.info(
        f"Attempting to allocate {allocation.value} to {allocation.description}."
    )
    amount = allocation.value
    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


def percentage_strategy(
    allocation: Allocation, remainder: Decimal, *_, **__
) -> Decimal:
    logging.info(
        f"Attempting to allocate {allocation.value}% to {allocation.description}."
    )
    amount = round(remainder * (allocation.value / 100), 2)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


all_strategies = dict(
    top_up=top_up_strategy,
    fixed=fixed_strategy,
    percentage=percentage_strategy,
)
