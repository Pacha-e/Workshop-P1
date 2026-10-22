from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movie.ai import generate_image, get_client
from movie.models import Movie


class Command(BaseCommand):
    help = "Generar con IA la imagen de la primera película y actualizar su campo image"

    def handle(self, *args, **options):
        images_folder = Path(settings.MEDIA_ROOT) / "movie/images"
        images_folder.mkdir(parents=True, exist_ok=True)
        movies = Movie.objects.order_by("pk")
        self.stdout.write(f"Found {movies.count()} movies")
        client = get_client()
        for movie in movies:
            content, source = generate_image(client, f"Movie poster of {movie.title}")
            filename = f"m_{movie.title}.png"
            (images_folder / filename).write_bytes(content)
            movie.image = f"movie/images/{filename}"
            movie.save(update_fields=["image"])
            self.stdout.write(f"Imagen generada con: {source}")
            self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))
            break  # No quitar: procesa solo la primera película
        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))
