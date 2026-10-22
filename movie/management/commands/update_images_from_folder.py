from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from movie.models import Movie


class Command(BaseCommand):
    help = "Asignar a cada película su imagen m_<título>.png de media/movie/images/"

    def handle(self, *args, **options):
        folder = Path(settings.MEDIA_ROOT) / "movie/images"
        if not folder.is_dir():
            raise CommandError(f"Carpeta no encontrada: {folder}")
        updated = missing = 0
        for movie in Movie.objects.order_by("pk"):
            filename = f"m_{movie.title}.png"
            if (folder / filename).is_file():
                movie.image = f"movie/images/{filename}"
                movie.save(update_fields=["image"])
                updated += 1
                self.stdout.write(f"Updated image: {movie.title}")
            else:
                missing += 1
                self.stdout.write(f"Sin imagen: {movie.title}")
        self.stdout.write(self.style.SUCCESS(f"Finished: {updated} imágenes asignadas. Sin imagen: {missing}."))
