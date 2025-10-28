
## Estructura de DynamoFlow

El proyecto está estructurado como un **paquete de Python**, con el objetivo de que pueda integrarse fácilmente en otros proyectos de mayor escala.
Gracias a esta organización, puede distribuirse mediante el **gestor de paquetes PIP**, facilitando su instalación y uso.

La estructura del paquete es la siguiente:

```
dynamo_flow/
├── __init__.py
├── record_context_manager.py
├── operations
│   ├── __init__.py
│   ├── contextual_field_validation.py
│   ├── normalize_amount_operation.py
│   └── operation.py
└── records
    ├── __init__.py
    ├── order_event_record.py
    ├── product_update_record.py
    └── record.py
```
---

## Patrón de diseño utilizado

DynamoFlow implementa el patrón de diseño **Strategy** en dos niveles:

1. **Operaciones (Operations)**  
2. **Tipos de registro (Records)**

#### 1. Operaciones

- **Contexto:** La clase `RecordContextManager`, que delega la ejecución a las operaciones registradas.  
- **Interfaz:** La clase abstracta `Operation`, dentro del subpaquete `operations`.  
- **Estrategias:** Las clases `ContextualFieldValidation` y `NormalizeAmountOperation`, también dentro del subpaquete `operations`.

#### 2. Tipos de registro

- **Contexto:** La clase `RecordContextManager`, que delega la ejecución a las operaciones por defecto definidas para cada tipo de registro.  
- **Interfaz:** La clase abstracta `Record`, dentro del subpaquete `records`.  
- **Estrategias:** Las clases `OrderEventRecord` y `ProductUpdateRecord`, donde se definen las operaciones por defecto asociadas a cada tipo de registro.

---

## Descripción de los archivos

- **`__init__.py`**  
  Archivo estándar que facilita la importación del paquete.

- **`record_context_manager.py`**  
  `RecordContextManager`: interfaz principal para el usuario. Gestiona las operaciones a aplicar sobre cada tipo de registro.

- **`operations/contextual_field_validation.py`**  
  `ContextualFieldValidation`: valida que un campo sea obligatorio y cumpla una condición.

- **`operations/normalize_amount_operation.py`**  
  `NormalizeAmountOperation`: normaliza valores numéricos a `float`, manejando separadores decimales (coma/punto) y símbolos de moneda.

- **`operations/operation.py`**  
  `Operation`: clase base abstracta para operaciones.

- **`records/order_event_record.py`**  
  `OrderEventRecord`: operaciones por defecto para registros de tipo `order_event`.

- **`records/product_update_record.py`**  
  `ProductUpdateRecord`: operaciones por defecto para registros de tipo `product_update`.

- **`records/record.py`**  
  `Record`: clase base abstracta para tipos de registro.

---

## Estilo de programación

El código sigue la **filosofía de Python**, priorizando la simplicidad, claridad y mantenibilidad.
Se emplean **Type Hints** para especificar los tipos esperados en parámetros y valores de retorno, y **Docstrings** para documentar clases, métodos y funciones, detallando su propósito, argumentos y valores devueltos.

---

## Beneficios de la arquitectura

Esta arquitectura, basada en paquetes y en el patrón Strategy, permite una solución robusta, flexible y fácilmente extensible.

- Para agregar una nueva operación, basta con crear un nuevo archivo en el subpaquete `operations` y definir la clase correspondiente.
- Para añadir un nuevo tipo de registro con operaciones por defecto, se crea un nuevo archivo dentro del subpaquete `records`.

**No es necesario modificar archivos existentes para extender la funcionalidad.**

---

## Justificación (respondiendo las preguntas del desafio python)

Comparando ventajas y desventajas con otros enfoques:

| Enfoque      | Ventajas | Desventajas |
| ----------- | ----------- | ----------- |
| Actual (Strategy + Paquetes)      | Robusto, flexible y facil de extender.       | Requiere crear nuevos archivos por cada operación o tipo de registro.|
| Lista de funciones puras   | Simples de crear y probar, sin necesidad de clases.   | Difícil de mantener; modificar una función puede afectar toda la lista.|
| eval() | Altamente dinámico, permite crear reglas complejas. | Riesgo de seguridad elevado al ejecutar código arbitrario. |

Para **NormalizeAmountOperation:**

1.¿Cómo se aseguraría de que esta operación sea verdaderamente flexible para cualquier campo numérico, y no solo para amount o price?

- Esto se logra con el atributo de la clase llamado `field_name`, el cual se pasa como un parámetro obligatorio al crear el objeto. Solo es necesario poner el nombre del campo al cual aplicar la operación.

2.¿Cómo manejaría el caso donde el campo a normalizar no existe en el registro?

- En el método `NormalizeAmountOperation.execute`, se valida la existencia del campo al inicio.
- Si el campo no está presente, se establece su valor como `None` y se registra una advertencia, permitiendo que el procesamiento continúe sin interrupciones.

--- 
## Ejemplos de uso

Registrar operaciones para un tipo de registro:

```python
from dynamo_flow import RecordContextManager
from dynamo_flow.operations import NormalizeAmountOperation, ContextualFieldValidation

record_manager = RecordContextManager()  
record_manager.register_context("order_event",[
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.match(r'^ORD\d+$',x)),
    ContextualFieldValidation(field_name="customer_name", required=True)
])
```

Cambiar las operaciones por defecto para un tipo de registro:

```python
from dynamo_flow import RecordContextManager
from dynamo_flow.operations import NormalizeAmountOperation, ContextualFieldValidation

record_manager = RecordContextManager()
record_manager.set_default_record("order_event",[
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id"),
    ContextualFieldValidation(field_name="customer_name", required=True)
])
```

Eliminar un tipo de registro con sus operaciones por defecto:

```python
from dynamo_flow import RecordContextManager

record_manager = RecordContextManager()
record_manager.delete_default_record('order_event')
```

Procesar registros con operaciones definidas por el usuario:

```python
import re
from dynamo_flow import RecordContextManager
from dynamo_flow.operations import NormalizeAmountOperation, ContextualFieldValidation

record_manager = RecordContextManager()
record_manager.register_context("order_event",[
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.match(r'^ORD\d+$',x)),
    ContextualFieldValidation(field_name="customer_name", required=True)
])
records = [
    {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25,12 EUR",        
        "timestamp": "2023-10-26T14:00:00Z"
    }
]
for record, logs in record_manager.process_stream(records, default=False):
    print(record, ' -> ', logs, '\n')
```

Procesar registros con operaciones por defecto:

```python
from dynamo_flow import RecordContextManager

record_manager = RecordContextManager()
records = [
    {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25,12 EUR",        
        "timestamp": "2023-10-26T14:00:00Z"
    }
]
for record, logs in record_manager.process_stream(records):
    print(record, ' -> ', logs, '\n')
```

Procesar registros combinando operaciones personalizadas y por defecto:

```python
import re
from dynamo_flow import RecordContextManager
from dynamo_flow.operations import NormalizeAmountOperation, ContextualFieldValidation

record_manager = RecordContextManager()
record_manager.set_default_record("order_event",[
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.match(r'^ORD\d+$',x)),
    ContextualFieldValidation(field_name="customer_name", required=True)
])

records = [
    {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25,12 EUR",        
        "timestamp": "2023-10-26T14:00:00Z"
    },
    {
        "__type__": "product_update",
        "product_sku": "SKU_P002",
        "price": None,
        "is_active": "False"
    }
]
for record, logs in record_manager.process_stream(records):
    print(record, ' -> ', logs, '\n')
```