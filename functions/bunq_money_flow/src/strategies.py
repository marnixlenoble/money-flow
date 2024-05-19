import logging
from decimal import Decimal

from lib.common_strategies import (
    _check_maximum_amount,
    _check_minimum_amount,
    _check_remainder,
)
from .transfer_flows import Transfer
from .types import BankClient


def top_up_strategy(
    transfer: Transfer, remainder: Decimal, bank_client: BankClient
) -> Decimal:
    logging.info(f"Attempting to top up {transfer.description} to {transfer.value}.")
    balance = bank_client.get_balance_by_iban(iban=transfer.target_iban)
    amount = transfer.value - balance
    if amount < 0:
        logging.info(f"\t Skipping transfer. Balance is already sufficient.")
        return Decimal(0)

    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=transfer.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=transfer.maximum_amount)
    if amount > 0:
        logging.info(f"\t Need transfer {amount} to {transfer.target_iban_name}.")

    return amount
