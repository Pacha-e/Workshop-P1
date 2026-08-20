from django.shortcuts import render

from .models import News


def news(request):
    news_items = News.objects.all().order_by("-date")
    return render(request, "news.html", {"news_items": news_items})
