import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

import build
import language


class EmployerSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.out = Path(self.temp_dir.name)
        for role_dir in (ROOT / "roles").iterdir():
            if not role_dir.is_dir():
                continue
            slug = role_dir.name
            for lang in language.langs(role_dir):
                (self.out / f"david-adegbola-{slug}-{lang}.pdf").write_bytes(b"pdf")
            (self.out / f"david-adegbola-{slug}.pdf").write_bytes(b"pdf")
        self.made = build.build(self.out)

    def test_root_does_not_list_roles_and_all_pages_are_noindex(self):
        root = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex">', root)
        self.assertNotIn("/r/", root)

        for slug in self.made:
            page = (self.out / "r" / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn(f"david-adegbola-{slug}.pdf", page)

    def test_language_downloads_follow_each_role_setting(self):
        for slug in self.made:
            role_dir = ROOT / "roles" / slug
            langs = language.langs(role_dir)
            page = (self.out / "r" / slug / "index.html").read_text(encoding="utf-8")
            positions = [
                page.index(f'href="../../david-adegbola-{slug}-{lang}.pdf"')
                for lang in langs
            ]
            self.assertEqual(positions, sorted(positions), slug)
            if langs == ["en"]:
                self.assertNotIn(f"david-adegbola-{slug}-fi.pdf", page)

    def test_merged_role_redirects_keep_legacy_pdf_names(self):
        name = "David Adegbola"
        redirects = build.redirects(self.out, self.made, name)
        mapping = json.loads((ROOT / "site" / "redirects.json").read_text(encoding="utf-8"))
        eligible = [
            old for old, new in mapping.items()
            if not old.startswith("_") and new in self.made and not (ROOT / "roles" / old).exists()
        ]
        if eligible:
            old = eligible[0]
            self.assertTrue(any(f"r/{old}/ ->" in entry for entry in redirects))
            self.assertTrue((self.out / "r" / old / "index.html").is_file())
            self.assertTrue((self.out / f"david-adegbola-{old}.pdf").is_file())

    def test_contact_values_are_html_escaped(self):
        markup = build.contact_html({
            "location": '<script>alert("x")</script>',
            "phone": "+358 46 800 7210",
            "email": "david@example.com",
        })
        self.assertNotIn("<script>", markup)
        self.assertIn("&lt;script&gt;", markup)


if __name__ == "__main__":
    unittest.main()
