from fastapi import FastAPI, Request
import os
import requests
from openai import OpenAI

# Pega a chave da OpenAI do ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")

# URL da Z-API sem o token na URL
url = "https://api.z-api.io/instances/3DF2E49A8C47E00D72D032C54B267657/send-text"

# Cria app FastAPI
app = FastAPI()

# Prompt de sistema
system_prompt = {
    "role": "system",
    "content": "Você é a Lia, vendedora simpática, carismática e direta da LK Vest Confecções. Você atende clientes via WhatsApp."
}

# Gatilhos de anúncio
gatilhos_anuncio = [
    "vi o anúncio", "anuncio", "anúncio", "vi seu anúncio", "vi seu anuncio",
    "meta", "facebook", "instagram"
]

# Envia mensagem pela Z-API com o header certo
def enviar_mensagem(numero, mensagem):
    payload = {
        "phone": numero,
        "message": mensagem
    }

    headers = {
        "Content-Type": "application/json",
        "Client-Token": "A563B92C42CBFFF5234438DF"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Falha ao enviar mensagem: {response.status_code}")
        print(response.text)

# Rota do webhook
@app.post("/webhook")
async def responder(request: Request):
    body = await request.json()
    print("📩 BODY RECEBIDO:", body)

    mensagem_cliente = body.get("message", "").lower()
    numero_cliente = body.get("phone", "")

    # Se a mensagem for de anúncio
    if any(p in mensagem_cliente for p in gatilhos_anuncio):
        resposta_meta = "Oi! Vi que você veio do anúncio. Posso te ajudar com as novidades da loja?"
        enviar_mensagem(numero_cliente, resposta_meta)
        return {"resposta": resposta_meta}

    # Gera resposta com OpenAI
    client = OpenAI(api_key=openai_api_key)

    historico = [
        system_prompt,
        {"role": "user", "content": mensagem_cliente}
    ]

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historico
    )

    mensagem_bot = resposta.choices[0].message.content

    if numero_cliente:
        enviar_mensagem(numero_cliente, mensagem_bot)

    return {"resposta": mensagem_bot}
