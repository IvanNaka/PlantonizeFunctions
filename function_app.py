import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import azure.functions as func
import json
import logging
import requests
import os
from pymongo import MongoClient

app = func.FunctionApp()

# Configuração da conexão com MongoDB
MONGO_CONNECTION_STRING = os.getenv(
    "MONGO_CONNECTION_STRING",
    "mongodb+srv://ivannakatani_db_user:4ATXzTJWIOvRlNek@plantonize-cluster.tytzrfd.mongodb.net/?retryWrites=true&w=majority&appName=plantonize-cluster&tlsInsecure=false&tls=true"
)
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "VOcFcd0JIZaWirT2")

# Nomes das coleções
COLLECTION_NOTAS_FISCAIS = os.getenv("NOTAS_FISCAIS_COLLECTION", "NotasFiscais")
COLLECTION_FATURAS = os.getenv("FATURAS_COLLECTION", "Faturas")
COLLECTION_MUNICIPIOS_ALIQUOTA = os.getenv("MUNICIPIOS_ALIQUOTA_COLLECTION", "MunicipiosAliquota")
COLLECTION_IMPOSTOS_RESUMO = os.getenv("IMPOSTOS_RESUMO_COLLECTION", "ImpostosResumo")

# Cliente MongoDB (reutilizável entre invocações)
mongo_client = None

def get_mongo_client():
    """Retorna uma conexão com MongoDB (singleton)"""
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MONGO_CONNECTION_STRING)
        logging.info("✅ Conexão com MongoDB estabelecida")
    return mongo_client

def get_mongo_db():
    """Retorna o banco de dados MongoDB"""
    client = get_mongo_client()
    return client[MONGO_DATABASE]

def get_notas_fiscais_collection():
    """Retorna a coleção de Notas Fiscais"""
    db = get_mongo_db()
    return db[COLLECTION_NOTAS_FISCAIS]

def get_faturas_collection():
    """Retorna a coleção de Faturas"""
    db = get_mongo_db()
    return db[COLLECTION_FATURAS]

def get_municipios_aliquota_collection():
    """Retorna a coleção de Municípios e Alíquotas"""
    db = get_mongo_db()
    return db[COLLECTION_MUNICIPIOS_ALIQUOTA]

def get_impostos_resumo_collection():
    """Retorna a coleção de Impostos Resumo"""
    db = get_mongo_db()
    return db[COLLECTION_IMPOSTOS_RESUMO]

@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="integracao-nf",
    connection="ServiceBusConnection"
)
def EnviarNFSEFunction(msg: func.ServiceBusMessage):
    try:
        body = msg.get_body().decode("utf-8")
        logging.info(f"Mensagem recebida do Service Bus: {body}")

        data = json.loads(body)

        payload = {
            "cityServiceCode": data.get("codigo_servico", "101"),
            "description": data.get("descricao", "Serviço prestado"),
            "servicesAmount": data.get("valor", 0),
            "borrower": {
                "federalTaxNumber": data.get("cpf_cnpj_cliente", "00000000000"),
                "name": data.get("cliente", "Cliente não informado"),
                "email": data.get("email", ""),
                "address": {
                    "country": "BRA",
                    "postalCode": data.get("cep", "00000000"),
                    "street": data.get("endereco", "Rua não informada"),
                    "number": data.get("numero", "0"),
                    "district": data.get("bairro", ""),
                    "city": {
                        "code": data.get("codigo_municipio", "3550308"),
                        "name": data.get("municipio", "São Paulo")
                    },
                    "state": data.get("uf", "SP")
                }
            }
        }

        api_key = 'TESTE'
        empresa_id = 123

        if not api_key or not empresa_id:
            raise Exception("❌ Variáveis de ambiente NFE_API_KEY ou NFE_COMPANY_ID não configuradas.")

        url = f"https://api.nfe.io/v1/companies/{empresa_id}/serviceinvoices"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {api_key}"
        }


        logging.info("➡️ Enviando NFSe para NFe.io...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logging.info(f"📤 Resposta NFe.io: {response.status_code}")

        # Atualizar status no MongoDB se o envio foi bem-sucedido
        try:
            collection = get_notas_fiscais_collection()
            
            # Buscar por _id ou numeroNota
            filtro = {}
            if data.get("_id"):
                filtro["_id"] = data.get("_id")
            elif data.get("numeroNota"):
                filtro["numeroNota"] = data.get("numeroNota")
            
            if filtro:
                resultado = collection.update_one(
                    filtro,
                    {"$set": {"status": "Emitido"}}
                )
                
                if resultado.modified_count > 0:
                    logging.info(f"Status atualizado para 'Emitido' no MongoDB: {filtro}")
                elif resultado.matched_count > 0:
                    logging.info(f"ℹNota já estava com status 'Emitido': {filtro}")
                else:
                    logging.warning(f"Nota fiscal não encontrada no MongoDB: {filtro}")
            else:
                logging.warning("Nenhum identificador (_id ou numeroNota) fornecido para atualizar no MongoDB")
                
        except Exception as e:
            logging.error(f"Erro ao atualizar status no MongoDB: {str(e)}")
            # Não interrompe o fluxo, apenas registra o erro

        email_destinatario = data.get("email", "")
        if not email_destinatario:
            logging.warning("Nenhum e-mail informado na mensagem, não foi possível enviar aviso.")
            return

        if response.status_code in (200, 201):
            assunto = "NFSe emitida com sucesso"
            mensagem = f"A NFSe do cliente {data.get('cliente')} foi emitida com sucesso."
        else:
            assunto = "❌ Falha ao emitir NFSe"
            mensagem = (
                f"Falha ao emitir NFSe para o cliente {data.get('cliente')}.\n\n"
                f"Código de status: {response.status_code}\n"
                f"Detalhes: {response.text}"
            )

        enviar_email(email_destinatario, assunto, mensagem)
        logging.info(f"📧 E-mail enviado para {email_destinatario}")

    except Exception as e:
        logging.error(f"❌ Erro geral na função: {e}")


@app.route(route="EnviarEmailFunction", auth_level=func.AuthLevel.ANONYMOUS)
def EnviarEmailFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("📨 Função HTTP de envio de e-mail acionada.")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("❌ Corpo da requisição inválido.", status_code=400)

    destinatario = req_body.get("destinatario")
    assunto = req_body.get("assunto")
    mensagem = req_body.get("mensagem")

    if not destinatario or not assunto or not mensagem:
        return func.HttpResponse(
            "❌ Campos obrigatórios: destinatario, assunto e mensagem.",
            status_code=400
        )

    try:
        enviar_email(destinatario, assunto, mensagem)
        return func.HttpResponse(f"📧 E-mail enviado para {destinatario}", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"❌ Erro ao enviar e-mail: {str(e)}", status_code=500)


def enviar_email(destinatario, assunto, mensagem):
    remetente = os.getenv("SMTP_USER", "vieira.rgabi@gmail.com")
    senha = os.getenv("SMTP_PASS", "mjhj qtfa dlhr qulk")
    servidor_smtp = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    porta = int(os.getenv("SMTP_PORT", 587))

    msg_email = MIMEMultipart()
    msg_email["From"] = remetente
    msg_email["To"] = destinatario
    msg_email["Subject"] = assunto
    msg_email.attach(MIMEText(mensagem, "plain"))

    with smtplib.SMTP(servidor_smtp, porta) as server:
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg_email)
