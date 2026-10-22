from django.core.management.base import BaseCommand, CommandError

from movie.ai import get_client, get_completion, model
from movie.models import Movie

INSTRUCTION = (
    "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
    "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
    "debe incluir el género de la película y cualquier información adicional que sirva "
    "para crear un sistema de recomendación. Responde solo con la descripción, "
    "sin introducción ni formato markdown."
)


class Command(BaseCommand):
    help = "Actualizar con IA la descripción de la primera película (solo una, para ahorrar API)"

    def handle(self, *args, **options):
        movies = Movie.objects.order_by("pk")
        self.stdout.write(f"Found {movies.count()} movies")
        client = get_client()
        for movie in movies:
            self.stdout.write(f"Processing: {movie.title} (modelo: {model('chat')})")
            prompt = f"{INSTRUCTION} Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
            description = get_completion(client, prompt)
            if not description:
                raise CommandError("La API no devolvió una descripción")
            self.stdout.write(f"Original Description: {movie.description}")
            self.stdout.write(f"Updated Description: {description}")
            movie.description = description
            movie.save(update_fields=["description"])
            self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title} (solo primera película)"))
            break  # No quitar: procesa solo la primera película
