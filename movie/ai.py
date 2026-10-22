import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError
from dotenv import load_dotenv
from openai import OpenAI


def get_client():
    load_dotenv(Path(settings.BASE_DIR) / "openAI.env", override=False)
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("openai_apikey")
    if not key:
        raise CommandError("Falta OPENAI_API_KEY (o openai_apikey) en el entorno; no se modificó la base de datos.")
    return OpenAI(api_key=key)
