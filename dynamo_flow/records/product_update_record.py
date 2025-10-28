from dynamo_flow.operations.operation import Operation
from .record import Record
from ..operations import ContextualFieldValidation
from ..operations import NormalizeAmountOperation

class ProductoUpdateRecord(Record):
    """
    Clase que representa al registro 'product_update' con todas las operaciones por defecto.

    Attributes:
        operations (list[Operation]): Lista de operaciones por defecto.   

    Operaciones por defecto:
        NormalizeAmountOperation(field_name="price")
        ContextualFieldValidation(field_name="product_sku", required=True)
        ContextualFieldValidation(field_name="is_active", required=True, condition=lambda x: x.lower() in ('true', 'false'))
    """

    def __init__(self):
        """Inicializa las operaciones por defecto"""
        self._operations = [
            NormalizeAmountOperation(field_name="price"),
            ContextualFieldValidation(field_name="product_sku", required=True),
            ContextualFieldValidation(field_name="is_active", required=True, condition=lambda x: x.lower() in ('true', 'false')),
        ]

    def process_record(self, record : dict[str, any]) -> tuple[dict[str, any], list]:
        logs = list()
        for operation in self._operations:
             record, new_logs = operation.execute(record)
             logs.extend(new_logs)
        return record, logs
    
    def set_operations(self, operations: list[Operation]):
        self._operations = operations