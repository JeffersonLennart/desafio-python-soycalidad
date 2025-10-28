from typing import Generator
from dynamo_flow.operations.operation import Operation
from .operations import NormalizeAmountOperation
from .operations import ContextualFieldValidation
from .records import OrderEventRecord
from .records import ProductoUpdateRecord

class RecordContextManager:
    """
    Clase principal responsable de registrar contextos de registro y procesar flujos de registros.

    Attributes:
        recod_config (dict[str, list[Operation]]): Diccionario de la lista de operaciones por cada tipo de registro
    """

    # Diccionario que asocia cada tipo de registro con su clase de operaciones por defecto.
    # Se definen como variable de clase porque no depende de una instancia en específico.
    _records_by_default = {
        "order_event": OrderEventRecord(),
        "product_update": ProductoUpdateRecord(),
    }

    def __init__(self, record_config: dict[str, list[Operation]] = {}):
        """Inicializa las operaciones por tipo de registro"""
        self.record_config = record_config

    def register_context(self, record_type: str, operations: list[Operation]):
        """
        Registra una lista de operaciones por tipo de registro.
        
        Args:
            record_type (str): Tipo de registro.
            operations (list[Operation]): Lista de operaciones para el registro.                    
        """
        self.record_config[record_type] = operations

    def process_stream(self, records: list[dict[str, any]], default: bool = True) -> Generator[dict[str, any], list]:
        """
        Procesa un iterable de registros, identificando el tipo de cada uno y aplicando las operaciones correspondientes.

        Cada registro puede tener operaciones asignadas manualmente o usar las operaciones predeterminadas definidas para su tipo. 
        El orden de ejecución de las operaciones respeta el orden en que fueron definidas, ya sea manualmente o por defecto.        

        Args:
            records (list[dict[str, any]]): lista de registros.
            default (bool): Si se van a aplicar las operaciones por defecto a los tipos de registro. Por defecto es True.
            
        Returns:
            Generator (Generator [dict[str, any], list]): Generador con el registro procesado y la lista de errores o advertencias.
        """
        for record in records:
            logs = list()
            record_type = record.get('__type__')            
            # Valida si el registro esta vacío o no tiene el formato valido
            if not record or not record_type:
                logs.append({
                    "type": "WARNING",                    
                    "message": f"El registro esta vacío o no tiene un formato valido."                
                })
                yield record, logs
                continue
            # Valida que el registro tiene operaciones asignadas manualmente o por defecto
            if record_type not in self.record_config or record_type not in RecordContextManager._records_by_default:
                logs.append({
                    "type": "WARNING",                    
                    "message": f"El registro no tiene operaciones asignadas."                
                })
                yield record, logs
                continue
            # Realiza las operaciones por defecto al registro
            if default:
                order_event_record = RecordContextManager._records_by_default.get(record_type)
                yield order_event_record.process_record(record)
            else:                
                # Realiza las operaciones asignadas manualmente al registro. 
                operations = self.record_config.get(record_type)
                for operation in operations:
                    record, new_logs = operation.execute(record)
                    logs.extend(new_logs)
                yield record, logs

    def set_default_record(self, record_type: str, operations: list[Operation]):
        """
        Cambia las operaciones por defecto para un determino tipo de registro.     

        Args:
            record_type (str): Tipo de registro.
            operations (list[Operation]): Nueva lista de operaciones por defecto.
        """
        default_record = RecordContextManager._records_by_default.get(record_type)
        # Verifica si record_type existe
        if default_record:
            default_record.set_operations(operations)
        else:
            raise Exception("El tipo de registro no existe.")
        
    def delete_default_record(self, record_type: str):
        """        
        Elimina el tipo de registro por defecto junto con sus operaciones.

        Args:
            record_type (str): Tipo de registro.            
        """
        # Verifica si record_type existe
        if record_type in RecordContextManager._records_by_default:
            del RecordContextManager._records_by_default[record_type]
        else:
            raise Exception("El tipo de registro no existe.")

if __name__ == '__main__':

    import re
    from pprint import pprint 

    records_example = [{
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25,12 EUR",        
        "timestamp": "2023-10-26T14:00:00Z"
    },{
        "__type__": "product_update",
        "product_sku": "SKU_P001",
        "price": "sdff",
        "is_active": "Trues"        
    }]
    
    record_manager = RecordContextManager()

    # Registrar operaciones manualmente
    record_manager.register_context("order_event",[
        NormalizeAmountOperation(field_name="amount"),
        ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.search(r'ORD\d+',x)),
        ContextualFieldValidation(field_name="customer_name", required=True)
    ])

    record_manager.register_context("product_update", [
        NormalizeAmountOperation(field_name="price"),
        ContextualFieldValidation(field_name="product_sku"),
        ContextualFieldValidation(field_name="is_active", required=True),
    ])

    # Ejecutar el proceso de records con operaciones ingresadas manualmente
    for i, (record, logs) in enumerate(record_manager.process_stream(records_example, default=False)):
        status = "INVÁLIDO" if len(logs) else "VALIDO"
        print(f"===================REGISTRO {i+1}: {status}===================")
        print("Registro:")
        pprint(record, sort_dicts=False)
        print("Logs:")
        pprint(logs, sort_dicts=False)        
    print('\n')
    # Ejecutar el proceso de records con operaciones por defecto
    for i, (record, logs) in enumerate(record_manager.process_stream(records_example)):
        status = "INVÁLIDO" if len(logs) else "VALIDO"
        print(f"===================REGISTRO {i+1}: {status}===================")
        print("Registro:")
        pprint(record, sort_dicts=False)
        print("Logs:")
        pprint(logs, sort_dicts=False)      