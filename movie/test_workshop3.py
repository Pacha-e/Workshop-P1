import csv
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase

from movie.models import Movie


class CsvDescriptionTests(TestCase):
    def test_updates_matching_title_only(self):
        Movie.objects.create(title="Carmencita", description="Antes", image="movie/images/default.jpg")
        Movie.objects.create(title="Otra", description="Intacta", image="movie/images/default.jpg")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "updated.csv"
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=["Title", "Updated Description"])
                writer.writeheader()
                writer.writerow({"Title": "Carmencita", "Updated Description": "Después"})
                writer.writerow({"Title": "Ausente", "Updated Description": "No existe"})
            call_command("update_movies_from_csv", csv_file=str(source))
        self.assertEqual(Movie.objects.get(title="Carmencita").description, "Después")
        self.assertEqual(Movie.objects.get(title="Otra").description, "Intacta")


class FirstMovieDescriptionTests(TestCase):
    @patch("movie.management.commands.update_descriptions.get_client")
    def test_updates_only_first_movie_using_api(self, get_client):
        first = Movie.objects.create(title="Uno", description="Antes", image="movie/images/default.jpg")
        second = Movie.objects.create(title="Dos", description="Sin tocar", image="movie/images/default.jpg")
        get_client.return_value.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Descripción generada"))
        ]
        call_command("update_descriptions")
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.description, "Descripción generada")
        self.assertEqual(second.description, "Sin tocar")
        get_client.return_value.chat.completions.create.assert_called_once()
