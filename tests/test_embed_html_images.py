import base64
import importlib.util
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skill" / "scripts" / "embed_html_images.py"


class ImageSourceCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return
        attributes = dict(attrs)
        self.sources.append(attributes.get("src", ""))


def collect_image_sources(html):
    collector = ImageSourceCollector()
    collector.feed(html)
    return collector.sources


class EmbedHtmlImagesTests(unittest.TestCase):
    def load_module(self):
        self.assertTrue(
            SCRIPT_PATH.is_file(),
            f"packaging script does not exist: {SCRIPT_PATH}",
        )
        spec = importlib.util.spec_from_file_location("embed_html_images", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_embeds_local_png_and_jpeg_without_changing_bytes(self):
        module = self.load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "deliverables" / "reader.html"
            target = root / "portable" / "reader.html"
            figures = root / "assets" / "figures"
            figures.mkdir(parents=True)
            source.parent.mkdir(parents=True)

            png_bytes = b"\x89PNG\r\n\x1a\nfixture-png"
            jpeg_bytes = b"\xff\xd8\xfffixture-jpeg\xff\xd9"
            (figures / "figure one.png").write_bytes(png_bytes)
            (figures / "figure-two.jpg").write_bytes(jpeg_bytes)
            source.write_text(
                '<!doctype html><html><head><meta charset="UTF-8"></head><body>'
                '<img src="../assets/figures/figure%20one.png">'
                "<img src='../assets/figures/figure-two.jpg'>"
                "</body></html>",
                encoding="utf-8",
            )

            count, size = module.build_self_contained_html(source, target)

            output = target.read_text(encoding="utf-8")
            sources = collect_image_sources(output)
            self.assertEqual(count, 2)
            self.assertEqual(size, target.stat().st_size)
            self.assertEqual(len(sources), 2)
            self.assertTrue(sources[0].startswith("data:image/png;base64,"))
            self.assertTrue(sources[1].startswith("data:image/jpeg;base64,"))
            self.assertEqual(base64.b64decode(sources[0].split(",", 1)[1]), png_bytes)
            self.assertEqual(base64.b64decode(sources[1].split(",", 1)[1]), jpeg_bytes)
            self.assertIn('<link rel="icon" href="data:,">', output)

    def test_preserves_an_existing_data_uri(self):
        module = self.load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "reader.html"
            target = root / "portable.html"
            data_uri = "data:image/png;base64,AA=="
            source.write_text(f'<img src="{data_uri}">', encoding="utf-8")

            count, _ = module.build_self_contained_html(source, target)

            self.assertEqual(count, 0)
            self.assertEqual(
                collect_image_sources(target.read_text(encoding="utf-8")),
                [data_uri],
            )

    def test_supports_in_place_packaging(self):
        module = self.load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "reader.html"
            image = root / "figure.png"
            image_bytes = b"\x89PNG\r\n\x1a\nin-place"
            image.write_bytes(image_bytes)
            source.write_text('<img src="figure.png">', encoding="utf-8")

            count, size = module.build_self_contained_html(source, source)

            embedded_src = collect_image_sources(source.read_text(encoding="utf-8"))[0]
            self.assertEqual(count, 1)
            self.assertEqual(size, source.stat().st_size)
            self.assertEqual(
                base64.b64decode(embedded_src.split(",", 1)[1]),
                image_bytes,
            )

    def test_missing_local_image_fails_without_writing_target(self):
        module = self.load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "reader.html"
            target = root / "portable.html"
            source.write_text('<img src="missing.png">', encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                module.build_self_contained_html(source, target)

            self.assertFalse(target.exists())

    def test_external_image_fails_without_writing_target(self):
        module = self.load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "reader.html"
            target = root / "portable.html"
            source.write_text(
                '<img src="https://example.com/figure.png">',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                module.build_self_contained_html(source, target)

            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
