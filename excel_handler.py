import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Carregar as credenciais do ambiente (Render -> Environment Variable)
google_credentials = os.environ.get("GOOGLE_CREDENTIALS")

if not google_credentials:
    raise Exception("⚠️ Erro: Variável de ambiente GOOGLE_CREDENTIALS não encontrada.")

# Converter string JSON em dicionário
creds_dict = json.loads(google_credentials)

# Definir escopos necessários
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Criar credenciais do Google a partir do JSON
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# Autenticar no Google Sheets
client = gspread.authorize(creds)

# ID da planilha (extraído do link que partilhaste)
SHEET_ID = "1oLn7e47NWpeBwTX71fJCQ8NAPPCEgLWaCBxVCKzxc-U"

# Abrir planilha
sheet = client.open_by_key(SHEET_ID).sheet1

# Funções úteis
def adicionar_pedido(data_pedido, cliente, contacto, produto, quantidade, data_entrega, observacoes, status):
    """Adiciona um novo pedido na planilha."""
    nova_linha = [data_pedido, cliente, contacto, produto, quantidade, data_entrega, observacoes, status]
    sheet.append_row(nova_linha)

def listar_pedidos():
    """Lê todos os pedidos da planilha."""
    return sheet.get_all_records()

def atualizar_status(linha, novo_status):
    """Atualiza o status de pagamento de um pedido."""
    # Exemplo: coluna 8 = "Status de Pagamento"
    sheet.update_cell(linha, 8, novo_status)
