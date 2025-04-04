from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests
from openai import OpenAI

# 🔑 Pegando as variáveis de ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")
zapi_token = os.getenv("ZAPI_KEY") or "A563B92C42CBFFF5234438DF"
zapi_instance_url = os.getenv("ZAPI_URL") or "https://api.z-api.io/instances/3DF2E49A8C47E00D72D032C54B267657/token/A563B92C42CBFFF5234438DF/send-text"

# 🏠 Criando a aplicacao FastAPI
app = FastAPI()

# 🤖 Identidade da Ariel
system_prompt = {
    "role": "system",
    "content": (
        "Você é a Ariel, vendedora de atacado, simpática, divertida, bem-humorada e muito empática da loja online LK Vest."
        " Sua missão é ajudar os clientes no WhatsApp de forma descontraída e acolhedora, sempre buscando vender com jeitinho."
        " Todas as vendas são feitas online, não temos loja física."
        " Se a cliente quiser compar no varejo, direciona com carinho e diz queas compras são feitas exclusivamente pelo site https://ladykmodas.com.br e dúvidas são tiradas pelo telefone 11989771609."
        " No atacado, o pedido mínimo é de 8 peças ou R$ 300,00."
        " A fábrica fica na Rua Nazareno, 145 - Itaquaquecetuba/SP."
        " Não temos loja física só online"
        " Você envia para todo o Brasil via ônibus no Brás, transportadoras ou correios."
        " Quando finalizar uma venda, você deve pedir o nome completo e o endereço com CEP para envio, e informar que o pagamento é via Pix no número 1197874899."
        " Depois disso, diga que o pedido será processado e encerre a conversa de forma gentil."
    )
}

# 💬 Lista de palavras que ativam o modo "veio do meta"
gatilhos_anuncio = ["anuncio", "anúncio", "meta", "instagram", "facebook"]

# 🚗 Produtos + sugestões de revenda
produtos_catalogo = {
    "Conjunto Belly": "Viscolycra, blusa + saia midi, tamanhos M e G. Atacado R$45, revenda sugerida R$80.",
    "Vestido Isa": "Manga curta, básico, ideal para o dia a dia. M e G. Atacado R$28, revenda sugerida R$60.",
    "Vestido Ravena": "Suplex, animal print, midi com babado. M, G e G1. Atacado R$45, revenda sugerida R$85.",
    "Body Manu": "Suplex com decote quadrado. M, G, GG. Atacado R$16, revenda sugerida R$35.",
    "Regata Aline": "Gola alta, malha encorpada. M, G, GG. Atacado R$14, revenda sugerida R$30."
}

# 📢 Função para envio de mensagem via ZAPI
def enviar_mensagem(numero, mensagem):
    payload = {"phone": numero, "message": mensagem}
    headers = {"Content-Type": "application/json", "Client-Token": zapi_token}
    response = requests.post(zapi_instance_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Erro ao enviar mensagem: {response.status_code}\n{response.text}")

# 🚫 Ignora mensagens de grupo e só responde no privado
def deve_responder(body):
    return not body.get("isGroup", False) and not body.get("broadcast", False)

# 🚀 Webhook
@app.post("/webhook")
async def responder(request: Request):
    body = await request.json()
    print("📩 BODY RECEBIDO:", body)

    if not deve_responder(body):
        print("🚫 Ignorando mensagem de grupo ou broadcast.")
        return {"status": "ignorado"}

    mensagem_cliente = body.get("text", {}).get("message", "").lower()
    numero_cliente = body.get("phone", "")

    if any(gatilho in mensagem_cliente for gatilho in gatilhos_anuncio):
        resposta_meta = (
            "Oi! Vi que você veio do nosso anúncio 😊 Estou aqui pra te ajudar com as novidades da LK Vest."
            "Já te adianto: tá no lugar certo pra renovar seu estoque com estilo e preço de atacado!"
            "Me conta o que você tá procurando hoje que eu te ajudo AGORA mesmo!"
        )
        enviar_mensagem(numero_cliente, resposta_meta)
        return {"resposta": resposta_meta}

    # 🤖 Chamada ao OpenAI
    client = OpenAI(api_key=openai_api_key)
    historico = [system_prompt, {"role": "user", "content": mensagem_cliente}]

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historico
    )

    mensagem_bot = resposta.choices[0].message.content
    print("🤖 RESPOSTA:", mensagem_bot)

    enviar_mensagem(numero_cliente, mensagem_bot)
    return {"resposta": mensagem_bot}

# 🔍 Rota viva para o Render/UptimeRobot
@app.get("/")
def ping():
    return JSONResponse(content={"status": "Ariel está online e pronta pra vender!"})
