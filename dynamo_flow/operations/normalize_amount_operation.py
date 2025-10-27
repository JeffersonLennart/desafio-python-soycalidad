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
    def dot_comma_number_to_float(number: str) -> float:
        """
        Convierte un número con punto/coma decimal, con/sin separadores de miles a float Python.
            
            Args:
                number: Número a transformar
                
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
    
    # Es estatico porque no depende de una instancia de la clase
    @staticmethod
    def number_to_float(number: str) -> float:
        """
        Convierte cualquier formato numérico (con punto/coma decimal, con/sin separadores de miles, con simbolos de monedas, en notación científica, etc) a float Python.
        
        Args:
            number: Número en cualquier formato
            
        Returns:
            float: El número convertido
        """
        number = str(number)
        # Verificar si el numero viene en notación científica
        scientific_notation = r'[+-]?\d+[\.,]?\d*[eE][+-]?\d+'
        if re.match(scientific_notation, number):            
            return float(number.replace(',', '.'))                            

        # Conserva solo dígitos, comas, puntos, guiones y abreviaciones
        number = re.sub(r'[^\d,.-]','', number)        
        
        # Numeros especiales que terminan en -. Ejm: 1.234,56-
        if number.endswith('-'):
            number = '-' + number[:-1]

        # Si no es un número
        if not number:
            return None
        
        return NormalizeAmountOperation.dot_comma_number_to_float(number)                

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
                "field": f"{field_name}",
                "message": f"El campo no existe."                
            })
        else:
            # Realizamos la conversión. Si falla registramos el log y establecemos el campo en None
            try:
                value_float = NormalizeAmountOperation.to_float(value)
                if value_float:
                    record[field_name] = value_float
                # Si value es None, entonces el campo no es un numero valido 
                else:
                    record[field_name] = None
                    logs.append({
                        "type": "WARNING",
                        "field": f"{field_name}",
                        "message": f"El campo no es un número."                    
                    })

            except Exception as e:
                record[field_name] = None
                logs.append({
                    "type": "ERROR",
                    "field": f"{field_name}",
                    "message": f"Error en la conversión: {e}"                    
                })

        return record, logs

if __name__ == '__main__':
    numeros_especiales = [
    "12345",    
    "$1,234.56",
    "€1.234,56",
    "1,234,567.89",
    "1.234.567,89",
    "(1.234,56)",
    "JPY 123,456",
    "1234,56",
    "1234.56",
    "£1,234.56",
    "¥123,456",
    "₹1,23,456.78",
    "R$ 1.234,56",
    "CHF 1'234.56",
    "kr 1 234,56",
    "₽1 234,56",
    "₪1,234.56",
    "฿1,234.56",
    "-$1,234.56",
    "($1,234.56)",
    "-1.234,56 €",
    "1.234,56-",
    "1,234.56-",
    "⟨1,234.56⟩",
    "+$1,234.56",
    "USD 1,234.56",
    "EUR 1.234,56",
    "GBP1,234.56",
    "MXN$1,234.56",
    "1,234,567,890.12",
    "0.0000123",
    "0,000001",
    ".50",
    ",50",
    "1.234e+6",
    "1,234E-3",
    "1234",
    "1 234.56",
    "1'234'567.89",
    "1.234",
    "12.345",
    "$1,234.56 USD",
    "1.234,56€",
    "123.456,78 EUR",
    "1,234.56 Cr",
    "1,234.56 Dr"    
    ]
    for i, value in enumerate(numeros_especiales):        
        print(value,"->", NormalizeAmountOperation.number_to_float(value))