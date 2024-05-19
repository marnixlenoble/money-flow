import logging
from abc import abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True)
class Flow:
    description: str
    value: Decimal
    strategy_type: str
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    priority: Optional[int] = 1

    @property
    @abstractmethod
    def source(self):
        ...

    @property
    @abstractmethod
    def target_label(self):
        ...

    @property
    @abstractmethod
    def action_label(self):
        ...


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


def fixed_strategy(flow: Flow, remainder: Decimal) -> Decimal:
    logging.info(
        f"Attempting to {flow.action_label} {flow.value} to {flow.description}."
    )
    amount = flow.value
    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=flow.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=flow.maximum_amount)
    if amount > 0:
        logging.info(f"\t Need to {flow.action_label} {amount} to {flow.target_label}.")

    return amount


def percentage_strategy(flow: Flow, remainder: Decimal) -> Decimal:
    logging.info(
        f"Attempting to {flow.action_label} {flow.value}% to {flow.description}."
    )
    amount = round(remainder * (flow.value / 100), 2)
    amount = _check_minimum_amount(amount, minimum_amount=flow.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=flow.maximum_amount)
    if amount > 0:
        logging.info(f"\t Need to {flow.action_label} {amount} to {flow.target_label}.")

    return amount


default_strategies = {
    "fixed": fixed_strategy,
    "percentage": percentage_strategy,
}
