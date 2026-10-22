import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from movie.models import Movie


DEFAULT_CSV = Path(__file__).resolve().parents[3] / "docs/taller3/material/updated_movie_descriptions.csv"


class Command(BaseCommand):
    help = "Actualizar descripciones coincidentes con el CSV entregado por el docente"

    def add_arguments(self, parser):
        parser.add_argument("--csv-file", type=Path, default=DEFAULT_CSV)

    def handle(self, *args, **options):
        source = Path(options["csv_file"])
        if not source.is_file():
            raise CommandError(f"CSV no encontrado: {source}")
        updated = missing = 0
        with source.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not {"Title", "Updated Description"}.issubset(reader.fieldnames):
                raise CommandError("El CSV requiere Title y Updated Description")
            for row in reader:
                title, description = row["Title"], row["Updated Description"]
                matches = Movie.objects.filter(title=title)
                count = matches.update(description=description)
                if count:
                    updated += count
                    self.stdout.write(f"Updated: {title}")
                else:
                    missing += 1
                    self.stdout.write(f"Sin coincidencia: {title}")
        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated} movies from CSV. Sin coincidencia: {missing}."))
