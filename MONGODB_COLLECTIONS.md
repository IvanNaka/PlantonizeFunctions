# Coleções MongoDB - Plantonize

## Configuração

O sistema está configurado para usar o MongoDB Atlas com as seguintes coleções:

- **NotasFiscais** - Notas fiscais emitidas
- **Faturas** - Faturas geradas
- **MunicipiosAliquota** - Alíquotas de ISS por município
- **ImpostosResumo** - Resumo de impostos

## Como Usar nas Functions

### 1. Notas Fiscais

```python
from function_app import get_notas_fiscais_collection

# Inserir uma nota fiscal
collection = get_notas_fiscais_collection()
nota = {
    "_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "numeroNota": "12345",
    "dataEmissao": datetime.now(),
    "valorTotal": 100.00,
    "status": "Autorizado",
    "medico": {
        "nome": "Dr. João",
        "cpfCnpj": "12345678900"
    }
}
collection.insert_one(nota)

# Atualizar status
collection.update_one(
    {"_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"},
    {"$set": {"status": "Emitido"}}
)

# Buscar notas
notas = collection.find({"status": "Emitido"})
```

### 2. Faturas

```python
from function_app import get_faturas_collection

collection = get_faturas_collection()

# Criar fatura
fatura = {
    "numeroFatura": "FAT-001",
    "dataVencimento": datetime.now(),
    "valorTotal": 1500.00,
    "status": "Pendente"
}
collection.insert_one(fatura)
```

### 3. Municípios e Alíquotas

```python
from function_app import get_municipios_aliquota_collection

collection = get_municipios_aliquota_collection()

# Buscar alíquota de um município
municipio = collection.find_one({"codigo": "3550308"})
aliquota = municipio.get("aliquotaIss", 0)
```

### 4. Impostos Resumo

```python
from function_app import get_impostos_resumo_collection

collection = get_impostos_resumo_collection()

# Inserir resumo de impostos
resumo = {
    "periodo": "2025-11",
    "totalIss": 150.00,
    "totalIrrf": 75.00,
    "totalInss": 110.00
}
collection.insert_one(resumo)
```

## Funções Auxiliares Disponíveis

- `get_mongo_client()` - Retorna o cliente MongoDB (singleton)
- `get_mongo_db()` - Retorna o banco de dados configurado
- `get_notas_fiscais_collection()` - Retorna a coleção de Notas Fiscais
- `get_faturas_collection()` - Retorna a coleção de Faturas
- `get_municipios_aliquota_collection()` - Retorna a coleção de Municípios/Alíquotas
- `get_impostos_resumo_collection()` - Retorna a coleção de Impostos Resumo

## Variáveis de Ambiente

Configure no `local.settings.json` ou nas Application Settings do Azure:

```json
{
  "MONGO_CONNECTION_STRING": "mongodb+srv://...",
  "MONGO_DATABASE": "VOcFcd0JIZaWirT2",
  "NOTAS_FISCAIS_COLLECTION": "NotasFiscais",
  "FATURAS_COLLECTION": "Faturas",
  "MUNICIPIOS_ALIQUOTA_COLLECTION": "MunicipiosAliquota",
  "IMPOSTOS_RESUMO_COLLECTION": "ImpostosResumo"
}
```
