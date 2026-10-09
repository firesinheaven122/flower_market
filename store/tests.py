import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from store.models import Category, Product


class SeedDemoCatalogTests(TestCase):
    def test_seed_creates_bouquets_and_images_without_duplicates(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch(
                    "store.management.commands.seed_demo_catalog.urlopen",
                    side_effect=lambda url, timeout: BytesIO(b"\xff\xd8\xffphoto"),
                ) as download_photo:
                    call_command("seed_demo_catalog", verbosity=0)
                    call_command("seed_demo_catalog", verbosity=0)

            self.assertEqual(Product.objects.count(), 10)
            self.assertEqual(Category.objects.count(), 5)
            self.assertEqual(download_photo.call_count, 10)
            for product in Product.objects.all():
                self.assertTrue(
                    Path(media_root, product.image.name).is_file(),
                    product.image.name,
                )
                self.assertEqual(Path(product.image.name).suffix, ".jpg")
