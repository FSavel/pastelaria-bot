import os
import logging
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from excel_handler import adicionar_pedido  # ✅ só esta importação é necessária

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

twilio_bp = Blueprint('twilio', __name__)

# Guardar estado de cada utilizador
user_state = {}

# Menu principal
def menu_principal():
    return (
        "Olá 👋, bem-vindo à *Padaria Papú!* 🥖\n\n"
        "Escolha uma opção:\n"
        "1️⃣ Ver Menu\n"
        "2️⃣ Promoções e Prato do Dia\n"
        "3️⃣ Fazer Reserva / Encomenda\n"
        "4️⃣ Contactar Atendimento\n\n"
        "Digite o número da opção desejada:"
    )

# Menu de produtos
def menu_produtos():
    return (
        "📋 *Menu de Hoje:*\n\n"
        "🍞 Pão Francês - 5MT\n"
        "🥐 Croissant - 20MT\n"
        "🍰 Bolo de Chocolate - 50MT\n"
        "🍔 Hamburger - 150MT\n\n"
        "👉 Para fazer uma reserva ou encomenda, volte ao menu principal e escolha a opção *3️⃣*.\n\n"
        "Digite 0️⃣ para voltar ao menu principal."
    )

@twilio_bp.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")

    logging.debug(f"Mensagem recebida de {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    state = user_state.get(from_number, {"step": "menu"})
    logging.debug(f"Estado atual do usuário {from_number}: {state}")

    # Etapas do fluxo
    if state["step"] == "menu":
        logging.debug("Entrou no passo MENU")
        if incoming_msg == "1":
            msg.body(menu_produtos())
        elif incoming_msg == "2":
            msg.body(
                "🔥 *Promoções de Hoje:*\n"
                "- Pão Francês: leve 10, pague 8!\n"
                "- Croissant: 15MT cada (promoção!)\n\n"
                "🍲 *Prato do Dia:*\n"
                "- Feijoada com arroz e salada - 250MT\n\n"
                "Digite 0️⃣ para voltar ao menu principal."
            )
        elif incoming_msg == "3":
            msg.body("📛 Digite o seu *nome* para a reserva:")
            state["step"] = "nome"
        elif incoming_msg == "4":
            msg.body("☎️ Atendimento: Ligue para +258 84 123 4567 ou responda aqui mesmo.")
        else:
            msg.body(menu_principal())

    elif state["step"] == "nome":
        logging.debug("Entrou no passo NOME")
        state["nome"] = incoming_msg
        msg.body("📞 Agora, digite o seu *contacto*:")
        state["step"] = "contacto"

    elif state["step"] == "contacto":
        logging.debug("Entrou no passo CONTACTO")
        state["contacto"] = incoming_msg
        msg.body("🍴 Qual é o *produto* que deseja reservar?")
        state["step"] = "produto"

    elif state["step"] == "produto":
        logging.debug("Entrou no passo PRODUTO")
        state["produto"] = incoming_msg
        msg.body("🔢 Informe a *quantidade*:")
        state["step"] = "quantidade"

    elif state["step"] == "quantidade":
        logging.debug("Entrou no passo QUANTIDADE")
        state["quantidade"] = incoming_msg
        msg.body("📅 Para quando deseja a sua encomenda? (Ex: Hoje às 17h, Amanhã, Sábado...)")
        state["step"] = "data_entrega"

    elif state["step"] == "data_entrega":
        logging.debug("Entrou no passo DATA_ENTREGA")
        if incoming_msg.strip() == "":
            msg.body("⚠️ Não recebi a data de entrega. Por favor, digite para quando deseja a sua encomenda (Ex: Hoje às 17h, Amanhã, Sábado...):")
        else:
            state["data_entrega"] = incoming_msg
            msg.body("📝 Alguma *observação* para a sua reserva?")
            state["step"] = "observacoes"

    elif state["step"] == "observacoes":
        logging.debug("Entrou no passo OBSERVACOES")
        state["observacoes"] = incoming_msg

        try:
            adicionar_pedido(
                state["nome"],
                state["contacto"],
                state["produto"],
                state["quantidade"],
                state["data_entrega"],
                obs=state["observacoes"],
                status="Pendente"
            )
            logging.debug("Pedido registrado com sucesso no Google Sheets")
        except Exception as e:
            logging.error(f"Erro ao gravar no Google Sheets: {e}")
            msg.body(f"❌ Erro ao registrar o pedido: {e}")
            user_state[from_number] = state
            return str(resp)

        msg.body(
            f"✅ Sua reserva foi registada com sucesso!\n"
            f"Obrigado, volte sempre. 🙏\n\n"
            f"📋 *Detalhes do Pedido:*\n"
            f"👤 Cliente: *{state['nome']}*\n"
            f"📞 Contacto: *{state['contacto']}*\n"
            f"🍴 Produto: *{state['produto']}*\n"
            f"🔢 Quantidade: *{state['quantidade']}*\n"
            f"📅 Data de Entrega: *{state['data_entrega']}*\n"
            f"📝 Observações: *{state['observacoes']}*\n\n"
            "💳 *Nota sobre o pagamento:*\n"
            "Em breve entraremos em contacto para confirmar os detalhes e a forma de pagamento. ✅\n\n"
            "Deseja fazer outra encomenda?\n"
            "1️⃣ Sim\n"
            "2️⃣ Não"
        )
        state["step"] = "nova_encomenda"

    elif state["step"] == "nova_encomenda":
        logging.debug("Entrou no passo NOVA_ENCOMENDA")
        if incoming_msg == "1":
            msg.body(menu_principal())
            state = {"step": "menu"}
        elif incoming_msg == "2":
            msg.body("✨ Foi um prazer atendê-lo. Até breve na Padaria Papú! 🥖")
            state = {"step": "menu"}
        else:
            msg.body("❓ Escolha uma opção válida:\n1️⃣ Sim\n2️⃣ Não")

    # Retornar ao menu
    if incoming_msg == "0":
        logging.debug("Voltou ao menu principal pelo comando 0")
        msg.body(menu_principal())
        state = {"step": "menu"}

    # Guardar estado
    user_state[from_number] = state
    logging.debug(f"Novo estado do usuário {from_number}: {state}")

    return str(resp)
