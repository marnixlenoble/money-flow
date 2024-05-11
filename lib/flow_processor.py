from decimal import Decimal
from itertools import groupby
from typing import Optional, Protocol

from .common_strategies import Flow
from .firestore import FireStore


class ClientAdapter(Protocol):
    def handle_processed_flow(self, flow: Flow, amount: Decimal) -> None:
        ...

    def get_balance(self, source: str) -> Decimal:
        ...


class FlowProcessor:
    def __init__(
        self, client_adapter: ClientAdapter, store: FireStore, strategies: dict
    ):
        self.client_adapter = client_adapter
        self.store = store
        self.strategies = strategies

    def run(self):
        flows_all = self.store.get_flows()
        flows_by_source = groupby(flows_all, key=lambda x: x.source)

        for source, group in flows_by_source:
            remainder = self.client_adapter.get_balance(source=source)
            flows_per_source = list(group)
            flows_per_source.sort(key=lambda x: x.priority)
            grouped_flows = groupby(flows_per_source, key=lambda x: x.priority)

            for _, group_ in grouped_flows:
                flows = list(group_)
                for flow in filter(lambda a: a.strategy_type != "percentage", flows):
                    remainder = self._process_flow(flow, remainder)

                original_remainder = remainder
                for flow in filter(lambda a: a.strategy_type == "percentage", flows):
                    remainder = self._process_flow(
                        flow,
                        remainder,
                        original_remainder=original_remainder,
                    )

    def _process_flow(
        self,
        flow: Flow,
        remainder: Decimal,
        *,
        original_remainder: Optional[Decimal] = None,
    ):
        strategy = self.strategies.get(flow.strategy_type)
        amount = strategy(
            flow,
            original_remainder if original_remainder else remainder,
            bank_client=self.client_adapter,
        )
        if amount > 0:
            self.client_adapter.handle_processed_flow(amount=amount, flow=flow)

        return remainder - amount
