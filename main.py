import re
from pprint import pprint
from dynamo_flow import RecordContextManager
from dynamo_flow.operations import NormalizeAmountOperation, ContextualFieldValidation

records = [
    # Validos
    {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "25,12 EUR",        
        "timestamp": "2023-10-26T14:00:00Z"
    },
    {
        "__type__": "product_update",
        "product_sku": "SKU_P001",
        "price": "99.99 EUR",
        "is_active": "True"        
    },
    {
        "__type__": "order_event",
        "order_id": "ORD789",
        "customer_name": "Luis Vargas",
        "amount": "123,45 EUR",
        "timestamp": "2024-10-26T14:00:00Z"
    },    
    # No validos
    {
        "__type__": "order_event",
        "order_id": "ORD100T",
        "customer_name": "Bob el Constructor",
        "amount": "no_es_un_numero",
        "timestamp": "2024-13-01T25:61:00Z"
    },
    {
        "__type__": "product_update",
        "product_sku": "SKU_P002",
        "price": None,
        "is_active": "False"
    },
    {
        "__type__": "product_update",
        "product_sku": "SKU_P003T",
        "price": "25.00",
        # 'is_active'
    },
    {},
]

# Mostrar ejecución con las operaciones por defecto por tipo de registro
def ejemplo_operaciones_defecto():    
    record_manager = RecordContextManager()    
    for i, (record, logs) in enumerate(record_manager.process_stream(records)):
        status = "INVÁLIDO" if len(logs) else "VALIDO"
        print(f"===================REGISTRO {i+1}: {status}===================")
        print("Registro:")
        pprint(record, sort_dicts=False)
        print("Logs:")
        pprint(logs, sort_dicts=False)   

# Mostrar ejecución con las operaciones definidas manualmente por tipo de registro
def ejemplo_operaciones_manuales():
    record_manager = RecordContextManager()
        
    record_manager.register_context("order_event",[
        NormalizeAmountOperation(field_name="amount"),
        ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.match(r'^ORD\d+$',x)),
        ContextualFieldValidation(field_name="customer_name", required=True)
    ])

    record_manager.register_context("product_update", [
        NormalizeAmountOperation(field_name="price"),
        ContextualFieldValidation(field_name="product_sku", required=True, condition=lambda x: re.match(r'^SKU_P\d+$',x)),
        ContextualFieldValidation(field_name="is_active", required=True, condition=lambda x: x.lower() in ('true', 'false')),
    ])
    
    for i, (record, logs) in enumerate(record_manager.process_stream(records, default=False)):
        status = "INVÁLIDO" if len(logs) else "VALIDO"
        print(f"===================REGISTRO {i+1}: {status}===================")
        print("Registro:")
        pprint(record, sort_dicts=False)
        print("Logs:")
        pprint(logs, sort_dicts=False)  

# Mostrar ejecución con las operaciones por defecto y definidas manualmente por tipo de registro
def ejemplo_operaciones_defecto_manuales():
    record_manager = RecordContextManager()
    # Cambiar las operaciones por defecto para el registro order_event y para product_update se usaran las por defecto
    record_manager.set_default_record("order_event",[
        NormalizeAmountOperation(field_name="amount"),
        ContextualFieldValidation(field_name="order_id", required=True, condition=lambda x: re.match(r'^ORD\d+$',x)),
        ContextualFieldValidation(field_name="customer_name", required=True)
    ])
    
    for i, (record, logs) in enumerate(record_manager.process_stream(records)):
        status = "INVÁLIDO" if len(logs) else "VALIDO"
        print(f"===================REGISTRO {i+1}: {status}===================")
        print("Registro:")
        pprint(record, sort_dicts=False)
        print("Logs:")
        pprint(logs, sort_dicts=False)          

# ejemplo_operaciones_defecto()
# ejemplo_operaciones_manuales()
ejemplo_operaciones_defecto_manuales()