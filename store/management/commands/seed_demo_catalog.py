from pathlib import Path
from urllib.request import urlopen

from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import Category, Product


BOUQUETS = (
    {
        "title": "Розовый рассвет",
        "slug": "pink-dawn",
        "category": "Розы",
        "description": "Пышные садовые розы нежно-розовых оттенков с эвкалиптом.",
        "price": "4900.00",
        "stock_quantity": 12,
    },
    {
        "title": "Алые чувства",
        "slug": "scarlet-feelings",
        "category": "Розы",
        "description": "Классические алые розы и сочная зелень для признания в чувствах.",
        "price": "5900.00",
        "stock_quantity": 8,
    },
    {
        "title": "Облачные пионы",
        "slug": "cloud-peonies",
        "category": "Пионы",
        "description": "Воздушные кремовые пионы с тонкими веточками зелени.",
        "price": "7200.00",
        "stock_quantity": 6,
    },
    {
        "title": "Солнечный день",
        "slug": "sunny-day",
        "category": "Сезонные",
        "description": "Жёлтые подсолнухи, ромашки и летнее настроение.",
        "price": "3600.00",
        "stock_quantity": 14,
    },
    {
        "title": "Лавандовый вечер",
        "slug": "lavender-evening",
        "category": "Авторские",
        "description": "Лавандовые розы и воздушные сезонные цветы в пастельной гамме.",
        "price": "5400.00",
        "stock_quantity": 9,
    },
    {
        "title": "Белый шёлк",
        "slug": "white-silk",
        "category": "Свадебные",
        "description": "Белоснежные цветы с кремовыми акцентами для особенного дня.",
        "price": "6800.00",
        "stock_quantity": 5,
    },
    {
        "title": "Малиновый зефир",
        "slug": "raspberry-marshmallow",
        "category": "Авторские",
        "description": "Пышные малиновые и нежно-розовые цветы с эвкалиптом.",
        "price": "4300.00",
        "stock_quantity": 10,
    },
    {
        "title": "Полевая история",
        "slug": "meadow-story",
        "category": "Сезонные",
        "description": "Ромашки, васильки и нежные полевые цветы, собранные вручную.",
        "price": "3200.00",
        "stock_quantity": 16,
    },
    {
        "title": "Персиковый сад",
        "slug": "peach-garden",
        "category": "Розы",
        "description": "Тёплые персиковые розы с нежными кремовыми бутонами.",
        "price": "5100.00",
        "stock_quantity": 7,
    },
    {
        "title": "Утренняя нежность",
        "slug": "morning-tenderness",
        "category": "Авторские",
        "description": "Микс розовых и белых садовых цветов с лёгкой зеленью.",
        "price": "4700.00",
        "stock_quantity": 11,
    },
)

PHOTO_URLS = {
    "pink-dawn": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/44/"
        "Rose_and_carnation_flower_bouquet_01.jpg/"
        "960px-Rose_and_carnation_flower_bouquet_01.jpg"
    ),
    "scarlet-feelings": (
        "https://upload.wikimedia.org/wikipedia/commons/3/32/"
        "Wedding_bouquet_red_reses.jpg"
    ),
    "cloud-peonies": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ef/"
        "Bouquet_of_peonies_12.JPG/960px-Bouquet_of_peonies_12.JPG"
    ),
    "sunny-day": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b1/"
        "A_bouquet_of_orange_tulips_on_a_table.jpg/"
        "960px-A_bouquet_of_orange_tulips_on_a_table.jpg"
    ),
    "lavender-evening": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1b/"
        "FLOWERS_Mixed_%282213955920%29.jpg/960px-FLOWERS_Mixed_%282213955920%29.jpg"
    ),
    "white-silk": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/49/"
        "Beach_Wedding_Bouquet.jpg/960px-Beach_Wedding_Bouquet.jpg"
    ),
    "raspberry-marshmallow": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/"
        "A_bouquet_of_Gerberas_on_Ermou_Street.jpg/"
        "960px-A_bouquet_of_Gerberas_on_Ermou_Street.jpg"
    ),
    "meadow-story": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/74/"
        "Poppies_bouquet_2017_G1.jpg/960px-Poppies_bouquet_2017_G1.jpg"
    ),
    "peach-garden": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/73/"
        "Orange_rose_bouquet_%28Unsplash%29.jpg/"
        "960px-Orange_rose_bouquet_%28Unsplash%29.jpg"
    ),
    "morning-tenderness": (
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d2/"
        "Bouquet_of_peonies_02.JPG/960px-Bouquet_of_peonies_02.JPG"
    ),
}


class Command(BaseCommand):
    help = "Creates sample bouquets with real flower photos."

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / "products"
        media_dir.mkdir(parents=True, exist_ok=True)

        categories = {
            name: Category.objects.get_or_create(
                slug=name.lower().replace(" ", "-"),
                defaults={"name": name},
            )[0]
            for name in ("Розы", "Пионы", "Сезонные", "Авторские", "Свадебные")
        }

        created_count = 0
        for bouquet in BOUQUETS:
            slug = bouquet["slug"]
            image_name = f"products/{slug}.jpg"
            image_path = media_dir / f"{slug}.jpg"
            if not image_path.exists():
                image_url = PHOTO_URLS[slug]
                with urlopen(image_url, timeout=30) as response:
                    image_data = response.read()

                if not image_data.startswith(b"\xff\xd8\xff"):
                    raise ValueError(f"Downloaded bouquet photo is not a JPEG: {image_url}")
                image_path.write_bytes(image_data)

            _, created = Product.objects.get_or_create(
                title=bouquet["title"],
                defaults={
                    "category": categories[bouquet["category"]],
                    "description": bouquet["description"],
                    "price": bouquet["price"],
                    "stock_quantity": bouquet["stock_quantity"],
                    "image": image_name,
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                product = Product.objects.get(title=bouquet["title"])
                if not product.image or product.image.name != image_name:
                    product.image = image_name
                    product.save(update_fields=["image"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Каталог готов: добавлено {created_count} новых букетов, "
                f"всего {Product.objects.filter(is_active=True).count()} активных."
            )
        )
