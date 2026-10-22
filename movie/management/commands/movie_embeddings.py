from django.core.management.base import BaseCommand

from movie.ai import get_client, get_embedding, model
from movie.models import Movie


class Command(BaseCommand):
    help = "Generar y almacenar los embeddings de todas las películas"

    def handle(self, *args, **options):
        client = get_client()
        movies = Movie.objects.order_by("pk")
        self.stdout.write(f"Found {movies.count()} movies in the database (modelo: {model('embedding')})")
        for movie in movies:
            try:
                movie.emb = get_embedding(client, movie.description).tobytes()
                movie.save(update_fields=["emb"])
                self.stdout.write(self.style.SUCCESS(f"✅ Embedding stored for: {movie.title}"))
            except Exception as error:
                self.stderr.write(f"❌ Failed to generate embedding for {movie.title}: {error}")
        self.stdout.write(self.style.SUCCESS("🎯 Finished generating embeddings for all movies"))
