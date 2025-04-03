from fastapi import FastAPI, Request
import openai
import os

openai.api_key = os.getenv("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")

app = FastAPI()

# System prompt padrão da Lia
system_prompt = {
    "role": "system",
    "content": "Você é a Lia, vendedora simpática, carismática e direta da LK Vest Confecções. Você atende com agilidade e um tom leve, divertido e profissional. Seja objetiva, evite enrolação e direcione sempre para a venda."
}

# Palavras-chave pra detectar leads do anúncio
gatilhos_anuncio = [
    "vi o anúncio", "anuncio", "anúncio", "vi seu anúncio", "vi seu anuncio", "meta", "facebook", "instagram"
]

resposta_meta = (
    "Oi, lindona! 👗 Que bom te ver por aqui! 💕 Vi que veio pelo nosso anúncio — já te adianto: "
    "tá no lugar certo pra renovar seu estoque com estilo e preço de atacado!\n\n"
    "Me conta o que você tá procurando hoje que eu te ajudo AGORA mesmo! 🚀"
)

@app.post("/webhook")
async def responder(request: Request):
    body = await request.json()
    mensagem_cliente = body.get("message", "").lower()

    # Verifica se veio do anúncio
    if any(palavra in mensagem_cliente for palavra in gatilhos_anuncio):
        return {"resposta": resposta_meta}

    # Caso contrário, segue o fluxo normal com o chat
    historico = [system_prompt]
    historico.append({"role": "user", "content": mensagem_cliente})

    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=historico
    )

    mensagem_bot = resposta.choices[0].message["content"]
    return {"resposta": mensagem_bot}
