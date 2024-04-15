import logging
import warnings
from decimal import Decimal
from time import sleep
from typing import Protocol, Optional

from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.api_environment_type import ApiEnvironmentType
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated.endpoint import MonetaryAccount, Payment
from bunq.sdk.model.generated.object_ import Amount, Pointer

warnings.filterwarnings("ignore", message=r".*bunq SDK beta.*")
logger = logging.getLogger(__name__)


class ApiContextLoader(Protocol):
    def save(self, api_context: ApiContext):
        ...

    def load(self) -> Optional[ApiContext]:
        ...


class BunqClient:
    def __init__(
        self,
        api_key,
        environment_type,
        device_description,
        api_context_loader: ApiContextLoader,
    ):
        self.api_key = api_key
        self.environment_type = (
            ApiEnvironmentType.PRODUCTION
            if environment_type == "production"
            else ApiEnvironmentType.SANDBOX
        )
        self.device_description = device_description
        self.api_context_loader = api_context_loader

        self.is_connected = False
        self._memoized_accounts = None

    def connect(self):
        api_context = self.api_context_loader.load()
        if api_context is None:
            logger.info("Creating new bunq api context")
            api_context = ApiContext.create(
                self.environment_type, self.api_key, self.device_description
            )
            self.api_context_loader.save(api_context)
        else:
            logger.info("Loaded existing bunq api context")

        session_changed = api_context.ensure_session_active()
        if session_changed:
            self.api_context_loader.save(api_context)

        BunqContext.load_api_context(api_context)
        self.is_connected = True

    def make_payment(
        self,
        *,
        amount: Decimal,
        description: str,
        iban: str,
        iban_name: str,
        account_id: int,
    ):
        if not self.is_connected:
            raise Exception("Not connected. Please call connect first")

        max_retries = 5
        retry_delay = 10
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(f"Making payment of {amount} to {iban} ({iban_name})")
                Payment.create(
                    amount=Amount("{:.2f}".format(amount), "EUR"),
                    counterparty_alias=Pointer("IBAN", iban, name=iban_name),
                    description=description,
                    monetary_account_id=account_id,
                )
                sleep(2)
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Payment failed: {e}")
                logger.info(f"Retrying... ({retry_count}/{max_retries})")
                sleep(retry_delay)

    def get_balance_by_id(self, *, id_: int):
        if not self.is_connected:
            raise Exception("Not connected. Please call connect first")

        main_account: MonetaryAccount = MonetaryAccount.get(id_).value
        if main_account is None or main_account.is_all_field_none():
            logger.error(f"Could not retrieve balance of account with id {id_}")
            return None

        return Decimal(main_account.get_referenced_object().balance.value)

    def get_balance_by_iban(self, *, iban: str):
        if not self.is_connected:
            raise Exception("Not connected. Please call connect first")

        if not self._memoized_accounts:
            self._memoized_accounts = MonetaryAccount.list().value

        accounts = self._memoized_accounts
        for account in accounts:
            if account.is_all_field_none():
                continue

            referenced_object = account.get_referenced_object()
            for alias in referenced_object.alias:
                if alias.type_ == "IBAN" and alias.value == iban:
                    return Decimal(referenced_object.balance.value)

        else:
            logger.error(f"Could not retrieve balance of account with iban {iban}")
