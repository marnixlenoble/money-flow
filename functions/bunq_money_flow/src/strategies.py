import logging
from decimal import Decimal

from lib.common_strategies import (
    _check_maximum_amount,
    _check_minimum_amount,
    _check_remainder,
    fixed_strategy,
    percentage_strategy,
)
from lib.flow_processor import ClientAdapter
from .transfer_flows import Transfer


def top_up_strategy(
    transfer: Transfer, remainder: Decimal, *, bank_client: ClientAdapter
) -> Decimal:
    logging.info(f"Attempting to top up {transfer.description} to {transfer.value}.")
    balance = bank_client.get_balance(source=transfer.target_iban)
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


all_strategies = dict(
    top_up=top_up_strategy,
    fixed=fixed_strategy,
    percentage=percentage_strategy,
)
