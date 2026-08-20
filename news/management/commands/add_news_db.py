import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from news.models import News


class Command(BaseCommand):
    help = "Load news from Fake.csv into the News model"

    def handle(self, *args, **kwargs):
        csv_file_path = "news/management/commands/Fake.csv"
        created_count = 0
        updated_count = 0

        try:
            with open(csv_file_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                imported_headlines = []

                for index, row in enumerate(reader):
                    if index == 5:
                        break

                    imported_headlines.append(row["title"])
                    obj, created = News.objects.update_or_create(
                        headline=row["title"],
                        defaults={
                            "body": row["text"],
                            "date": datetime.strptime(row["date"], "%B %d, %Y").date(),
                        },
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                News.objects.exclude(headline__in=imported_headlines).delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import completed. "
                    f"Created: {created_count}, "
                    f"Updated: {updated_count}"
                )
            )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {exc}"))
