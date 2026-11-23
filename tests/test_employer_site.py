import json
import os
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
        os.environ.pop("DOWNLOADS_PATH", None)
        os.environ.pop("APPLICATIONS_DIR", None)
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
            self.assertIn(build.cv_file_name(slug), page)
            self.assertNotIn(f"david-adegbola-{slug}", page)
            self.assertTrue((self.out / build.cv_file_name(slug)).is_file())

    def test_language_downloads_follow_each_role_setting(self):
        for slug in self.made:
            role_dir = ROOT / "roles" / slug
            langs = language.langs(role_dir)
            page = (self.out / "r" / slug / "index.html").read_text(encoding="utf-8")
            positions = [
                page.index(f'href="../../{build.cv_file_name(slug, lang)}"')
                for lang in langs
            ]
            self.assertEqual(positions, sorted(positions), slug)
            if langs == ["en"]:
                self.assertNotIn(build.cv_file_name(slug, "fi"), page)

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


    def test_downloads_page_only_at_secret_path_and_lists_every_role(self):
        self.assertEqual([p for p in self.out.iterdir() if p.is_dir() and p.name != "r"], [])
        os.environ["DOWNLOADS_PATH"] = "test-secret-path-1234"
        self.addCleanup(os.environ.pop, "DOWNLOADS_PATH", None)
        build.build(self.out)
        page = (self.out / "test-secret-path-1234" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex">', page)
        for slug in self.made:
            self.assertIn(f"../{build.cv_file_name(slug)}", page)
            self.assertIn(f'href="cv/{slug}/"', page)
            view = (self.out / "test-secret-path-1234" / "cv" / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'data="../../../{build.cv_file_name(slug)}', view)
        self.assertNotIn("/r/", page)  # no public employer page links on the private page
        self.assertIn('role="tablist"', page)
        self.assertIn("cv-applications/issues/new?template=new-job.yml", page)
        self.assertNotIn("test-secret-path-1234", (self.out / "index.html").read_text(encoding="utf-8"))
        root = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="owner"', root)  # the owner's code box is there, without the code

    def test_downloads_page_lists_cover_letters_from_the_private_checkout(self):
        apps = Path(self.temp_dir.name) / "apps"
        (apps / "role-a-company-city").mkdir(parents=True)
        (apps / "role-a-company-city" / "cover-letter-combined.pdf").write_bytes(b"pdf")
        (apps / "role-a-company-city" / "cover-letter-fi.pdf").write_bytes(b"pdf")
        (apps / "role-a-company-city" / "email-fi.txt").write_text("Hakemus: Rooli A\n\nHei,\n\nhaen <työtä>.\n", encoding="utf-8")
        (apps / "role-a-company-city" / "cover-letter-en.tex").write_text(
            "\\recipient{1 May 2026}{Someone}\n\\subject{Application: Role A, 0--40 h/week, Company City}\n", encoding="utf-8")
        (apps / "job-details").mkdir()
        for key, value in {"DOWNLOADS_PATH": "test-secret-path-1234", "APPLICATIONS_DIR": str(apps)}.items():
            os.environ[key] = value
            self.addCleanup(os.environ.pop, key, None)
        build.build(self.out)
        page = (self.out / "test-secret-path-1234" / "index.html").read_text(encoding="utf-8")
        self.assertIn("letters/role-a-company-city/David-Adegbola-Cover-Letter-Role-A.pdf", page)
        self.assertTrue((self.out / "test-secret-path-1234" / "letters" / "role-a-company-city" / "David-Adegbola-Cover-Letter-Role-A-FI.pdf").is_file())
        self.assertNotIn("job-details", page)
        self.assertIn("Role A, 0\u201340 h/week, Company City", page)
        self.assertIn("1 May 2026", page)
        self.assertIn('download="David-Adegbola-Cover-Letter-Role-A.pdf"', page)
        self.assertIn('download="David-Adegbola-Cover-Letter-Role-A-FI.pdf"', page)
        self.assertIn('download="David-Adegbola-CV-Warehouse-Worker.pdf"', page)
        self.assertNotIn('download="david-adegbola-', page)
        view = (self.out / "test-secret-path-1234" / "letters" / "role-a-company-city" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data="David-Adegbola-Cover-Letter-Role-A.pdf', view)
        self.assertIn('id="s-fi">Hakemus: Rooli A</b>', view)
        self.assertIn("haen &lt;työtä&gt;.", view)  # the text is escaped
        self.assertIn('letters/role-a-company-city/#email', page)
        self.assertIn('<meta name="robots" content="noindex">', view)
        self.assertIn('href="letters/role-a-company-city/"', page)
        self.assertNotIn("role-a-company-city", (self.out / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
