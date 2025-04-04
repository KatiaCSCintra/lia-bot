from fastapi import FastAPI, Request
import os
import requests
from openai import OpenAI

# 🔐 Inicializa o cliente OpenAI com a API key do Render (variável de ambiente)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# 🤖 Prompt base da Lia
system_prompt = {
    "role": "system",
    "content": (
        "Você é a Lia, vendedora simpática, carismática e direta da LK Vest Confecções. "
        "Você atende clientes pelo WhatsApp e ajuda a responder dúvidas ou realizar vendas."
    ),
}

# 🎣 Gatilhos que detectam mensagens de anúncio
gatilhos_anuncio = [
    "vi o anúncio", "anuncio", "anúncio", "vi seu anúncio", "vi seu anuncio",
    "meta", "facebook", "instagram"
]

resposta_meta = "Olá! Vi que você veio pelo nosso anúncio. Como posso te ajudar hoje?"

# 📤 Envia a mensagem pro número via API externa
def enviar_mensagem(numero, mensagem):
    url = "https://sua.api.whatsapp.fake/enviar"  # 🚨 Substitua pela sua URL real
    payload = {
        "numero": numero,
        "mensagem": mensagem
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Falha ao enviar mensagem: {response.status_code}")
        print(response.text)

# 📩 Webhook que recebe as mensagens
@app.post("/webhook")
async def responder(request: Request):
    body = await request.json()
    mensagem_cliente = body.get("message", "").lower()
    numero_cliente = body.get("phone", "")

    # 🎯 Detecta se veio do anúncio
    if any(p in mensagem_cliente for p in gatilhos_anuncio):
        enviar_mensagem(numero_cliente, resposta_meta)
        return {"resposta": resposta_meta}

    # 🤝 Resposta normal com OpenAI
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
