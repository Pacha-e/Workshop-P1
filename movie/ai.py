import base64
import os
from pathlib import Path
from urllib.parse import quote

import numpy as np
import requests
from django.conf import settings
from django.core.management.base import CommandError
from dotenv import load_dotenv
from openai import OpenAI

# Modelos del Taller 3 (OpenAI). Con AI_PROVIDER=gemini se usan los equivalentes de Gemini
# a través de su endpoint compatible con la librería de OpenAI.
MODELS = {
    "openai": {"chat": "gpt-3.5-turbo", "embedding": "text-embedding-3-small", "image": "dall-e-2"},
    "gemini": {"chat": "gemini-2.5-flash", "embedding": "gemini-embedding-001", "image": "gemini-2.5-flash-image"},
}
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"
EMBEDDING_DIMENSIONS = 1536


def _load_env():
    load_dotenv(Path(settings.BASE_DIR) / "openAI.env", override=False)


def provider():
    _load_env()
    name = os.environ.get("AI_PROVIDER", "openai").lower()
    if name not in MODELS:
        raise CommandError(f"AI_PROVIDER no soportado: {name}")
    return name


def model(kind):
    return MODELS[provider()][kind]


def _gemini_key():
    return os.environ.get("gemini_apikey") or os.environ.get("GEMINI_API_KEY")


def get_client():
    if provider() == "gemini":
        key = _gemini_key()
        if not key:
            raise CommandError("Falta gemini_apikey (o GEMINI_API_KEY) en el entorno.")
        return OpenAI(api_key=key, base_url=GEMINI_BASE_URL + "openai/")
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("openai_apikey")
    if not key:
        raise CommandError("Falta OPENAI_API_KEY (o openai_apikey) en el entorno; no se modificó la base de datos.")
    return OpenAI(api_key=key)


def get_completion(client, prompt):
    response = client.chat.completions.create(
        model=model("chat"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def get_embedding(client, text):
    response = client.embeddings.create(input=[text], model=model("embedding"), dimensions=EMBEDDING_DIMENSIONS)
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def generate_image(client, prompt):
    """Devuelve (bytes_de_la_imagen, origen)."""
    if provider() == "openai":
        response = client.images.generate(model=model("image"), prompt=prompt, size="256x256", quality="standard", n=1)
        image = requests.get(response.data[0].url, timeout=60)
        image.raise_for_status()
        return image.content, model("image")

    response = requests.post(
        f"{GEMINI_BASE_URL}models/{model('image')}:generateContent",
        headers={"x-goog-api-key": _gemini_key()},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=120,
    )
    if response.ok:
        for part in response.json()["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                return base64.b64decode(part["inlineData"]["data"]), model("image")
    # La capa gratuita de Gemini no incluye generación de imágenes (HTTP 429): respaldo sin API key.
    image = requests.get(
        f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=256&height=256&nologo=true", timeout=120
    )
    image.raise_for_status()
    return image.content, f"pollinations.ai (Gemini respondió HTTP {response.status_code})"
