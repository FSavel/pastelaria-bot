import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from whatsapp_bot import twilio_bp  # Importa o blueprint

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Criar app Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "papu_bakery_secret_key_2024")

# Corrigir proxy (Render precisa disto para HTTPS/WSGI)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Registar blueprint
app.register_blueprint(twilio_bp)

# Rota de teste (opcional)
@app.route("/")
def home():
    return "🚀 WhatsApp Bot da Padaria Papú está a funcionar!"

# Início da aplicação
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
