from fastapi import FastAPI, Request
import openai
import os
import requests

openai.api_key = os.getenv("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")

app = FastAPI()

# Prompt base da Lia
system_prompt = {
    "role": "system",
    "content": "Você é a Lia, vendedora simpática, carismática e direta da LK Vest Confecções. Você atende os clientes pelo WhatsApp com mensagens curtas e animadas."
}

gatilhos_anuncio = [
    "vi o anúncio", "anuncio", "anúncio", "vi seu anúncio", "vi seu anuncio", 
    "meta", "facebook", "instagram"
]

resposta_meta = (
    "Oi, lindona! 👗 Que bom te ver por aqui! 💕 Vi que veio pelo nosso anúncio — já te adianto: "
    "tá no lugar certo pra renovar seu estoque com estilo e preço de atacado!\n\n"
    "Me conta o que você tá procurando hoje que eu te ajudo AGORA mesmo! 💅"
)

def enviar_mensagem(numero, mensagem):
    url = f"https://api.z-api.io/instances/SEU_INSTANCE_ID/token/SEU_TOKEN/send-text"
    payload = {
        "phone": numero,
        "message": mensagem
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Falha ao enviar mensagem: {response.status_code}")
        print(response.text)

@app.post("/webhook")
async def responder(request: Request):
    body = await request.json()
    mensagem_cliente = body.get("message", "").lower()
    numero_cliente = body.get("phone", "")

    if any(p in mensagem_cliente for p in gatilhos_anuncio):
        enviar_mensagem(numero_cliente, resposta_meta)
        return {"resposta": resposta_meta}

    historico = [
        system_prompt,
        {"role": "user", "content": mensagem_cliente}
    ]

    client = openai.OpenAI()
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historico
    )
    mensagem_bot = resposta.choices[0].message.content

    if numero_cliente:
        enviar_mensagem(numero_cliente, mensagem_bot)

    return {"resposta": mensagem_bot}
