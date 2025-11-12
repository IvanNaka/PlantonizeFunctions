"""
Exemplo de como usar a conexão MongoDB nas suas Azure Functions
"""

from pymongo import MongoClient
import os

# Exemplo 1: Inserir um documento
def exemplo_insert():
    from function_app import get_mongo_db
    
    db = get_mongo_db()
    collection = db['notas_fiscais']
    
    documento = {
        "numero_nf": "12345",
        "cliente": "João Silva",
        "valor": 1500.00,
        "status": "emitida"
    }
    
    result = collection.insert_one(documento)
    print(f"Documento inserido com ID: {result.inserted_id}")


# Exemplo 2: Buscar documentos
def exemplo_find():
    from function_app import get_mongo_db
    
    db = get_mongo_db()
    collection = db['notas_fiscais']
    
    # Buscar todos
    documentos = collection.find()
    for doc in documentos:
        print(doc)
    
    # Buscar com filtro
    doc = collection.find_one({"numero_nf": "12345"})
    print(doc)


# Exemplo 3: Atualizar documento
def exemplo_update():
    from function_app import get_mongo_db
    
    db = get_mongo_db()
    collection = db['notas_fiscais']
    
    result = collection.update_one(
        {"numero_nf": "12345"},
        {"$set": {"status": "cancelada"}}
    )
    print(f"Documentos modificados: {result.modified_count}")


# Exemplo 4: Deletar documento
def exemplo_delete():
    from function_app import get_mongo_db
    
    db = get_mongo_db()
    collection = db['notas_fiscais']
    
    result = collection.delete_one({"numero_nf": "12345"})
    print(f"Documentos deletados: {result.deleted_count}")


# Exemplo 5: Usar dentro de uma Azure Function
"""
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="sua-queue",
    connection="ServiceBusConnection"
)
def MinhaFunction(msg: func.ServiceBusMessage):
    from function_app import get_mongo_db
    
    body = msg.get_body().decode("utf-8")
    data = json.loads(body)
    
    # Salvar no MongoDB
    db = get_mongo_db()
    collection = db['logs']
    collection.insert_one({
        "mensagem": data,
        "timestamp": datetime.now(),
        "processado": True
    })
    
    logging.info("✅ Dados salvos no MongoDB")
"""
