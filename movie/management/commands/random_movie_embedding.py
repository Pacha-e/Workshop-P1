import numpy as np
from django.core.management.base import BaseCommand, CommandError

from movie.models import Movie


class Command(BaseCommand):
    help = "Mostrar el embedding almacenado de una película al azar"

    def handle(self, *args, **options):
        movie = Movie.objects.order_by("?").first()
        if movie is None:
            raise CommandError("No hay películas en la base de datos")
        embedding = np.frombuffer(movie.emb, dtype=np.float32)
        self.stdout.write(f"🎬 Película al azar: {movie.title}")
        self.stdout.write(f"📐 Dimensión del embedding: {embedding.shape[0]}")
        self.stdout.write(f"🔢 Primeros 10 valores: {np.array2string(embedding[:10], precision=5)}")
        self.stdout.write(f"📏 Norma: {np.linalg.norm(embedding):.4f}")
