import re
from operation import Operation

class NormalizeAmountOperation(Operation):
    """
    Clase para normalizar un campo numérico.
    Convierte a float, manejando diferentes separadores y símbolos.    
    """
    
    def __init__(self, field_name:str, target_type:str = ""):
        super().__init__(field_name=field_name, target_type=target_type)

    # Es estatico porque no depende de una instancia de la clase
    @staticmethod
    def to_float(number: str) -> float:
        """
        Convierte cualquier formato numérico (punto/coma decimal, con/sin separadores de miles) 
        a float Python.
        
        Args:
            number: String con el número en cualquier formato
            
        Returns:
            float: El número convertido
        """
        
        # Caso 1: Cuando esta presente un unico separador (coma o punto) o ninguno
        dot_count = number.count('.')
        comma_count = number.count(',')        

        # Sin comas ni puntos    
        if dot_count == 0 and comma_count == 0:
            return float(number)

        # Con punto decimal. Ejem: 123.45
        if dot_count == 1 and comma_count == 0:            
            return float(number)
        
        # Con coma decimal. Ejem: 123,45
        if comma_count == 1 and dot_count == 0:            
            return float(number.replace(',', '.'))

        # Caso 2: Cuando esta presente ambos separadores (coma y punto)
        last_dot = number.rfind('.')
        last_comma = number.rfind(',')

        # Con coma para miles y punto para decimal. Ejem: 1,234.56
        if last_dot > last_comma:            
            return float(number.replace(',', ''))
        else:
        # Con punto para miles y coma para decimal. Ejem: 1.234,56
            return float(number.replace('.', '').replace(',', '.'))

    def execute(self, record : dict[str, any]) -> tuple:
        logs = list()
        # Recuperamos el field_name y verificamos si existe en el record
        field_name = self.parameters.get('field_name')
        value = record.get(field_name)
        # Si el campo no existe establecemos en None y registramos el log
        if value is None:
            record[field_name] = None
            logs.append({
                "type": "WARNING",
                "message": f"El campo '{field_name}' no existe."                
            })
        else:
            # Realizamos la conversión. Si falla registramos el log y establecemos el campo en None
            try:
                value = str(value)
                # Conserva solo dígitos, comas y puntos                
                value = re.sub(r'[^\d,.-]','', value)
                if value:
                    value_float = NormalizeAmountOperation.to_float(value)
                    record[field_name] = value_float
                # Si value esta vacio, entonces el campo no es un numero valido                
                else:
                    record[field_name] = None
                    logs.append({
                        "type": "WARNING",
                        "message": f"El campo '{field_name}' no es un número."                    
                    })

            except Exception as e:
                record[field_name] = None
                logs.append({
                    "type": "ERROR",
                    "message": f"Fallo al convertir el campo '{field_name}' a float. Error: {e}"                    
                })

        return record, logs


x = NormalizeAmountOperation(field_name="amount")
print(x.execute({"amounts":"1234"}))
