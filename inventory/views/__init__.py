# STOCK
from .stock import (
    stockmovement_list,
    stockmovement_create,
    export_stockmovements_csv,
)

# TRANSFERS
from .transfers import (
    transfer_list,
    transfer_create,
    transfer_detail,
    transfer_confirm,
    transfer_cancel,
)

# IMPORTS
from .imports import (
    import_stock_view,
    import_stock_confirm_view,
)

# ORDERS
from .orders import (
    order_list,
    order_create,
    order_detail,
    order_edit,
    order_send,
    order_receive,
    order_cancel,
    orders_counter,
)