# Datasets

The two CSV datasets used to populate the database are **not tracked in Git**. Together they
weigh about 105 MB, which is past GitHub's 50 MB warning threshold and would permanently bloat
the repository history. They are listed in `.gitignore` (`*.csv`).

Place them manually before running the seed commands.

## 1. `movies_initial.csv` (~42 MB)

Provided with Taller 2 in EAFIT Interactiva Virtual.

**Destination:** `movie/management/commands/movies_initial.csv`

Expected header:

```
imdbID,title,year,rating,runtime,genre,released,director,writer,cast,metacritic,imdbRating,imdbVotes,poster,plot,fullplot,language,country,awards,lastupdated,type
```

Only `title`, `year`, `genre` and `plot` are read by the seed command, and only the first 100
rows are imported.

Then run:

```bash
python manage.py add_movies_db
```

## 2. `Fake.csv` (~62 MB)

Download from Kaggle:
https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset

**Destination:** `news/management/commands/Fake.csv`

Expected header:

```
title,text,subject,date
```

The `date` column arrives as `Month DD, YYYY` (for example `December 31, 2017`) and is parsed
with `datetime.strptime(row['date'], '%B %d, %Y').date()`. Only the first 5 rows are imported.

Then run:

```bash
python manage.py add_news_db
```

## Verifying placement

```bash
ls -lh movie/management/commands/movies_initial.csv news/management/commands/Fake.csv
head -1 movie/management/commands/movies_initial.csv
head -1 news/management/commands/Fake.csv
```

Compare the two headers against the ones listed above before running the seed commands.
