from django.core.management.base import BaseCommand

from movie.ai import cosine_similarity, get_client, get_embedding, model
from movie.models import Movie

# Cambia estas películas y el prompt para probar otras combinaciones
MOVIE1_TITLE = "Frankenstein"
MOVIE2_TITLE = "The Great Train Robbery"
PROMPT = "película de terror sobre un científico que crea un monstruo"


class Command(BaseCommand):
    help = "Comparar dos películas y un prompt usando embeddings y similitud de coseno"

    def handle(self, *args, **options):
        client = get_client()
        movie1 = Movie.objects.get(title=MOVIE1_TITLE)
        movie2 = Movie.objects.get(title=MOVIE2_TITLE)
        self.stdout.write(f"Modelo de embeddings: {model('embedding')}")

        emb1 = get_embedding(client, movie1.description)
        emb2 = get_embedding(client, movie2.description)
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"🎬 Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

        prompt_emb = get_embedding(client, PROMPT)
        self.stdout.write(f"📝 Prompt: '{PROMPT}'")
        self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': {cosine_similarity(prompt_emb, emb1):.4f}")
        self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': {cosine_similarity(prompt_emb, emb2):.4f}")
