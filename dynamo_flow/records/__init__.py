from .order_event_record import OrderEventRecord
from .product_update_record import ProductoUpdateRecord

# Para poder importar las clases facilmente desde fuera del subpaquete records
__all__ = ['OrderEventRecord', 'ProductoUpdateRecord']