# Exemplos de Mensagens para Service Bus

## 📨 Como usar estes exemplos

Estes arquivos JSON são exemplos de mensagens que podem ser enviadas para a fila `integracao-nf` do Azure Service Bus para acionar a função `EnviarNFSEFunction`.

## 📋 Campos do JSON

### Campos Obrigatórios/Recomendados:

- **_id**: ID único da nota fiscal no MongoDB (para atualização de status)
- **numeroNota**: Número da nota fiscal
- **codigo_servico**: Código do serviço (padrão: "101")
- **descricao**: Descrição do serviço prestado
- **valor**: Valor total do serviço
- **cpf_cnpj_cliente**: CPF ou CNPJ do cliente (tomador)
- **cliente**: Nome do cliente
- **email**: Email do cliente (para envio de notificação)

### Campos de Endereço:

- **cep**: CEP do cliente
- **endereco**: Nome da rua/avenida
- **numero**: Número do endereço
- **bairro**: Bairro
- **codigo_municipio**: Código IBGE do município
- **municipio**: Nome do município
- **uf**: Sigla do estado (SP, RJ, MG, etc.)

## 🧪 Testando localmente

### 1. Usando Azure Storage Explorer ou Azure Portal:
- Envie o conteúdo de um dos arquivos JSON para a fila `integracao-nf`

### 2. Usando Azure CLI:
```bash
az servicebus queue message send \
  --queue-name integracao-nf \
  --body @exemplo_mensagem_service_bus.json \
  --namespace-name <seu-namespace>
```

### 3. Usando código Python:
```python
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json

# Ler o arquivo JSON
with open('exemplo_mensagem_service_bus.json', 'r') as f:
    mensagem = json.load(f)

# Enviar para o Service Bus
connection_string = "Endpoint=sb://..."
queue_name = "integracao-nf"

with ServiceBusClient.from_connection_string(connection_string) as client:
    sender = client.get_queue_sender(queue_name)
    with sender:
        message = ServiceBusMessage(json.dumps(mensagem))
        sender.send_messages(message)
        print("✅ Mensagem enviada!")
```

## 📁 Arquivos de Exemplo

1. **exemplo_mensagem_service_bus.json** - Consulta médica em São Paulo
2. **exemplo_mensagem_2.json** - Exame laboratorial em São Paulo
3. **exemplo_mensagem_3.json** - Procedimento cirúrgico no Rio de Janeiro

## ⚙️ O que acontece ao enviar:

1. ✅ A função `EnviarNFSEFunction` é acionada
2. 📤 NFSe é enviada para a API NFe.io
3. 💾 Status é atualizado no MongoDB para "Emitido" (se sucesso)
4. 📧 Email de notificação é enviado ao cliente

## 🔍 Valores Padrão

Se algum campo não for fornecido, os seguintes valores padrão serão usados:

- **codigo_servico**: "101"
- **descricao**: "Serviço prestado"
- **valor**: 0
- **cpf_cnpj_cliente**: "00000000000"
- **cliente**: "Cliente não informado"
- **cep**: "00000000"
- **endereco**: "Rua não informada"
- **numero**: "0"
- **codigo_municipio**: "3550308" (São Paulo)
- **municipio**: "São Paulo"
- **uf**: "SP"
