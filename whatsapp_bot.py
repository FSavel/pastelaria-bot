import os
import logging
from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from excel_handler import adicionar_pedido

logging.basicConfig(level=logging.DEBUG)

twilio_bp = Blueprint('twilio', __name__)

user_state = {}

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

def menu_produtos():
    return (
        "📋 *Menu de Hoje:*\n\n"
        "🍞 Pão Francês - 5MT\n"
        "🥐 Croissant - 20MT\n"
        "🍰 Bolo de Chocolate - 50MT\n"
        "🍔 Hamburger - 150MT\n\n"
        "Digite 0️⃣ para voltar ao menu principal."
    )

@twilio_bp.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")

    resp = MessagingResponse()
    msg = resp.message()

    state = user_state.get(from_number, {"step": "menu"})

    # MENU
    if state["step"] == "menu":
        if incoming_msg == "1":
            msg.body(menu_produtos())

        elif incoming_msg == "2":
            msg.body(
                "🔥 *Promoções de Hoje:*\n"
                "- Pão Francês: leve 10, pague 8!\n"
                "- Croissant: 15MT cada\n\n"
                "🍲 *Prato do Dia:*\n"
                "- Feijoada - 250MT\n\n"
                "Digite 0️⃣ para voltar."
            )

        elif incoming_msg == "3":
            msg.body("📛 Digite o seu *nome*:")
            state["step"] = "nome"

        elif incoming_msg == "4":
            msg.body("☎️ Atendimento: +258 84 123 4567")

        else:
            msg.body(menu_principal())

    # NOME
    elif state["step"] == "nome":
        if incoming_msg == "":
            msg.body("⚠️ Nome inválido. Digite novamente:")
        else:
            state["nome"] = incoming_msg
            msg.body("📞 Digite o seu *contacto* (apenas números):")
            state["step"] = "contacto"

    # CONTACTO
    elif state["step"] == "contacto":
        if not incoming_msg.isdigit():
            msg.body("⚠️ Contacto inválido. Use apenas números:")
        else:
            state["contacto"] = incoming_msg
            msg.body("🍴 Qual produto deseja?")
            state["step"] = "produto"

    # PRODUTO
    elif state["step"] == "produto":
        if incoming_msg == "":
            msg.body("⚠️ Produto inválido. Digite novamente:")
        else:
            state["produto"] = incoming_msg
            msg.body("🔢 Quantidade (apenas números):")
            state["step"] = "quantidade"

    # QUANTIDADE
    elif state["step"] == "quantidade":
        if not incoming_msg.isdigit():
            msg.body("⚠️ Quantidade inválida. Digite apenas números:")
        else:
            state["quantidade"] = incoming_msg
            msg.body("📅 Data de entrega:")
            state["step"] = "data_entrega"

    # DATA
    elif state["step"] == "data_entrega":
        if incoming_msg == "":
            msg.body("⚠️ Data inválida. Digite novamente:")
        else:
            state["data_entrega"] = incoming_msg
            msg.body("📝 Observações:")
            state["step"] = "observacoes"

    # OBSERVAÇÕES
    elif state["step"] == "observacoes":
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
        except Exception as e:
            msg.body("❌ Erro ao guardar pedido.")
            return str(resp)

        msg.body(
            f"✅ Pedido registado!\n\n"
            f"👤 {state['nome']}\n"
            f"📞 {state['contacto']}\n"
            f"🍴 {state['produto']}\n"
            f"🔢 {state['quantidade']}\n"
            f"📅 {state['data_entrega']}\n\n"
            "1️⃣ Nova encomenda\n2️⃣ Sair"
        )
        state["step"] = "nova"

    # NOVA
    elif state["step"] == "nova":
        if incoming_msg == "1":
            msg.body(menu_principal())
            state = {"step": "menu"}
        elif incoming_msg == "2":
            msg.body("Obrigado! 🙏")
            state = {"step": "menu"}
        else:
            msg.body("Escolha 1 ou 2.")

    # VOLTAR AO MENU
    if incoming_msg == "0":
        msg.body(menu_principal())
        state = {"step": "menu"}

    user_state[from_number] = state
    return str(resp)
