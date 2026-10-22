import csv
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
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


class ImagesFromFolderTests(TestCase):
    def test_assigns_existing_image_only(self):
        with tempfile.TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            folder = Path(media) / "movie/images"
            folder.mkdir(parents=True)
            (folder / "m_Uno.png").write_bytes(b"png")
            Movie.objects.create(title="Uno", description="x", image="movie/images/default.jpg")
            Movie.objects.create(title="Dos", description="x", image="movie/images/default.jpg")
            call_command("update_images_from_folder")
        self.assertEqual(Movie.objects.get(title="Uno").image.name, "movie/images/m_Uno.png")
        self.assertEqual(Movie.objects.get(title="Dos").image.name, "movie/images/default.jpg")


class EmbeddingTests(TestCase):
    @patch("movie.management.commands.movie_embeddings.get_embedding")
    @patch("movie.management.commands.movie_embeddings.get_client")
    def test_stores_embedding_as_float32_bytes(self, get_client, get_embedding):
        get_embedding.return_value = np.ones(1536, dtype=np.float32)
        movie = Movie.objects.create(title="Uno", description="x", image="movie/images/default.jpg")
        call_command("movie_embeddings")
        movie.refresh_from_db()
        self.assertTrue(np.array_equal(np.frombuffer(movie.emb, dtype=np.float32), np.ones(1536)))

    @patch("movie.views.get_embedding")
    @patch("movie.views.get_client")
    def test_recommendation_returns_most_similar_movie(self, get_client, get_embedding):
        Movie.objects.create(title="Cerca", description="x", image="movie/images/default.jpg",
                             emb=np.array([1, 0], dtype=np.float32).tobytes())
        Movie.objects.create(title="Lejos", description="x", image="movie/images/default.jpg",
                             emb=np.array([0, 1], dtype=np.float32).tobytes())
        get_embedding.return_value = np.array([0.9, 0.1], dtype=np.float32)
        response = self.client.get("/recommendations/", {"prompt": "algo"})
        self.assertEqual(response.context["movie"].title, "Cerca")
