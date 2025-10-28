from abc import ABC, abstractmethod
from dynamo_flow.operations.operation import Operation

class Record(ABC):
    """
    Clase abstracta para todos los tipos de registro con operaciones por defecto.
    """

    @abstractmethod
    def process_record(self, record : dict[str, any]) -> tuple[dict[str, any], list]:
        """
        Procesa un tipo de registro aplicando todas las operaciones por defecto.

        Args:
            record (dict[str, any]): El registro a procesar.
        
        Returns:
            tuple: Una tupla conteniendo:
                - dict[str, any]: Registro modificado.
                - list: Lista de advertencias o errores.
        """
        pass
    
    @abstractmethod
    def set_operations(self, operations: list[Operation]):
        """
        Cambia las operaciones por defecto

        Args:
            operations (list[Operation]): Nueva lista de operaciones por defecto.
        """
        pass