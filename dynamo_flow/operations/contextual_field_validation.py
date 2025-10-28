from typing import Callable
from .operation import Operation

class ContextualFieldValidation(Operation):
    """
    Clase para asegurar que un campo existe o es obligatorio y cumple con una condición dada.

    Attributes:
        field_name (str): El campo donde se aplicara esta operación.
        required (bool): Si el campo es obligatorio. Por defecto es True.
        condition (Callable[[any], bool]): La condición que debe cumplir el campo. Por defecto valida que no sea None.
        target_type (str): Tipo de registro donde se aplica esta operación. Por defecto esta vacío.
    """
    
    def __init__(self, field_name: str, required: bool = True, condition: Callable[[any], bool] = lambda x: x is not None and x != '', target_type: str = ""):
        super().__init__(field_name=field_name, required=required, condition=condition, target_type=target_type)  

    def execute(self, record : dict[str, any]) -> tuple:
        logs = list()
        # Recuperamos los atributos de la operación y el valor del campo en operación
        field_name = self.parameters.get('field_name')
        required = self.parameters.get('required')
        condition = self.parameters.get('condition')        
        value = record.get(field_name)
        # Si el campo es obligatorio validamos su existencia y que cumpla la condición
        if required:
            if value is None:
                logs.append({
                    "type": "WARNING",
                    "operation": self.__class__.__name__,
                    "field": f"{field_name}",
                    "message": f"El campo no está presente o es None."
                })
            else:
                try:                    
                    # Se verifica si se cumple la condición                    
                    if not condition(value):                    
                        logs.append({
                            "type": "WARNING",
                            "operation": self.__class__.__name__,
                            "field": f"{field_name}",
                            "message": f"El campo no cumple la condición.",
                        })
                except Exception as e:
                    logs.append({
                        "type": "ERROR",
                        "operation": self.__class__.__name__,
                        "field": f"{field_name}",
                        "message": f"Error al ejecutar la condición: {e}"
                    })
        
        return record, logs


if __name__ == '__main__':
    import re
    record_example = {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25.00",        
        "timestamp": "2023-10-26T14:00:00Z"
    }

    operation = ContextualFieldValidation("order_id", required=True, condition=lambda x: re.search(r'ORD\d+',x))
    record, logs = operation.execute(record_example)
    print(record)
    print(logs)