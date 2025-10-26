from abc import ABC, abstractmethod

class Operation(ABC):
    """
    Clase abstracta para todas las operaciones.
    """
    def __init__(self, **kwargs):
        """
        Inicializa los parámetros de cada operación como field_name o target_type.
        """
        self.parameters = kwargs

    @abstractmethod
    def execute(self, record : dict[str, any]) -> tuple:
        """
        Ejecuta la operación a un record (registro).

        Args:
            record: El registro a procesar.
        
        Returns:
            tuple:
                - record: Posiblemente modificado
                - logs: Lista de advertencias o errores.
        """
        pass