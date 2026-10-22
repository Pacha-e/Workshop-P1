from django.core.management.base import BaseCommand, CommandError

from movie.ai import get_client
from movie.models import Movie


class Command(BaseCommand):
    help = "Enriquecer con OpenAI la descripción de una sola película"

    def handle(self, *args, **options):
        movie = Movie.objects.order_by("pk").first()
        if movie is None:
            raise CommandError("No hay películas en la base de datos")
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": (
                "Describe de forma breve, precisa y en español la película "
                f"'{movie.title}' para un catálogo. Género: {movie.genre}. "
                f"Descripción previa: {movie.description}"
            )}],
            temperature=0,
        )
        description = response.choices[0].message.content
        if not description or not description.strip():
            raise CommandError("La API no devolvió una descripción")
        movie.description = description.strip()
        movie.save(update_fields=["description"])
        self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title} (solo primera película)"))
