import base64
from collections import Counter
from io import BytesIO

import matplotlib
from django.db.models import Count
from django.shortcuts import render

from .models import Movie

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

# Create your views here.


def home(request):
    searchTerm = request.GET.get("searchMovie")
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(
        request,
        "home.html",
        {"name": "Emmanuel Hernández", "searchTerm": searchTerm, "movies": movies},
    )


def about(request):
    return render(request, "about.html")


def statistics_view(request):
    movies_by_year = (
        Movie.objects.values("year")
        .annotate(total=Count("id"))
        .order_by("year")
    )
    year_labels = [
        str(item["year"]) if item["year"] is not None else "None"
        for item in movies_by_year
    ]
    year_totals = [item["total"] for item in movies_by_year]

    first_genres = [
        genre.split(",")[0].strip() or "Unknown"
        for genre in Movie.objects.values_list("genre", flat=True)
    ]
    movies_by_genre = Counter(first_genres).most_common()
    genre_labels = [genre for genre, _total in movies_by_genre]
    genre_totals = [total for _genre, total in movies_by_genre]

    return render(
        request,
        "statistics.html",
        {
            "year_chart": _bar_chart(
                year_labels,
                year_totals,
                "Movies by year",
                "Year",
                "Movies",
            ),
            "genre_chart": _bar_chart(
                genre_labels,
                genre_totals,
                "Movies by genre",
                "Genre",
                "Movies",
            ),
        },
    )


def _bar_chart(labels, values, title, x_label, y_label):
    fig = Figure(figsize=(10, 4.8), dpi=110)
    ax = fig.subplots()
    ax.bar(labels, values, color="#4dabf7")
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.6, alpha=0.5)
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    return base64.b64encode(buffer.getvalue()).decode("ascii")
