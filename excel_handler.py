import os
import gspread
from google.oauth2 import service_account
from datetime import datetime

# Carregar credenciais do Render (JSON armazenado em variável de ambiente)
google_creds = os.getenv("GOOGLE_CREDENTIALS")
if not google_creds:
    raise Exception("⚠️ A variável de ambiente GOOGLE_CREDENTIALS não foi encontrada.")

# Converter string JSON em dicionário
import json
creds_dict = json.loads(google_creds)

# Autenticar com gspread
credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(credentials)

# ID da tua planilha (pego da URL)
SHEET_ID = "1oLn7e47NWpeBwTX71fJCQ8NAPPCEgLWaCBxVCKzxc-U"
sheet = gc.open_by_key(SHEET_ID).sheet1


def adicionar_pedido(cliente, contacto, produto, quantidade, data_entrega, obs="", status="Pendente"):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo_pedido = [agora, cliente, contacto, produto, quantidade, data_entrega, obs, status]
    sheet.append_row(novo_pedido)
    return True


def listar_pedidos():
    return sheet.get_all_records()
