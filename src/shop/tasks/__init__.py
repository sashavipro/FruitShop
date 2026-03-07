"""src/shop/tasks/__init__.py."""

from .apples import trade_buy_apples
from .apples import trade_sell_apples
from .apricots import trade_buy_apricots
from .apricots import trade_sell_apricots
from .bananas import trade_buy_bananas
from .bananas import trade_sell_bananas
from .kiwi import trade_buy_kiwi
from .kiwi import trade_sell_kiwi
from .manual import trade_manual
from .oranges import trade_buy_oranges
from .oranges import trade_sell_oranges
from .peaches import trade_buy_peaches
from .peaches import trade_sell_peaches
from .pineapples import trade_buy_pineapples
from .pineapples import trade_sell_pineapples
from .warehouse import warehouse_audit_task

__all__ = (
    "trade_buy_apples",
    "trade_buy_apricots",
    "trade_buy_bananas",
    "trade_buy_kiwi",
    "trade_buy_oranges",
    "trade_buy_peaches",
    "trade_buy_pineapples",
    "trade_manual",
    "trade_sell_apples",
    "trade_sell_apricots",
    "trade_sell_bananas",
    "trade_sell_kiwi",
    "trade_sell_oranges",
    "trade_sell_peaches",
    "trade_sell_pineapples",
    "warehouse_audit_task",
)
