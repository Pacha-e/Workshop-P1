from django.db import models
import numpy as np


def get_default_array():
    return np.random.rand(1536).astype(np.float32).tobytes()

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="movie/images/")
    url = models.URLField(blank=True)
    emb = models.BinaryField(default=get_default_array)

    def __str__(self):
        return self.title
