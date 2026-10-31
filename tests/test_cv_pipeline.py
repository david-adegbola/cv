import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MONTHS_FI = "tammi|helmi|maalis|huhti|touko|kesä|heinä|elo|syys|loka|marras|joulu"
MONTHS_EN = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
EXPECTED_DATE = {
    "fi": re.compile(rf"^(?:{MONTHS_FI}) \d{{4}}--(?:(?:{MONTHS_FI}) \d{{4}}|nykyhetki)$", re.I),
    "en": re.compile(rf"^(?:{MONTHS_EN}) \d{{4}}--(?:(?:{MONTHS_EN}) \d{{4}}|present)$", re.I),
}
ONE_PAGE_ROLES = {"industrial-master", "warehouse-master"}
XHTML = "{http://www.w3.org/1999/xhtml}"


def cv_sources():
    for role_dir in sorted((ROOT / "roles").iterdir()):
        if not role_dir.is_dir():
            continue
        for source in sorted(role_dir.glob("cv-*.tex")):
            yield role_dir, source


def date_entries(source):
    return re.findall(r"\\begin\{cventry\}\{([^}]*)\}", source.read_text(encoding="utf-8"))


def normalized(text):
    text = re.sub(r"\s+", " ", text).strip().lower()
    return re.sub(r"[‐‑‒–—−]", "-", text)


def extract_pdf(pdf, layout=False):
    command = ["pdftotext", "-bbox-layout"] if layout else ["pdftotext"]
    result = subprocess.run(
        [*command, str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


class CvSourceTests(unittest.TestCase):
    def test_all_experience_dates_use_localized_month_names(self):
        source_count = 0
        for role_dir, source in cv_sources():
            source_count += 1
            language = source.stem.removeprefix("cv-")
            self.assertIn(language, EXPECTED_DATE, source)
            entries = date_entries(source)
            self.assertTrue(entries, source)
            for value in entries:
                self.assertRegex(value, EXPECTED_DATE[language], f"{source}: {value}")
        self.assertGreater(source_count, 0)


@unittest.skipUnless(shutil.which("pdftotext"), "Poppler pdftotext is required for PDF checks")
class CompiledCvTests(unittest.TestCase):
    def test_compiled_pdfs_have_dates_on_job_lines_and_fit_page_limits(self):
        for role_dir, source in cv_sources():
            language = source.stem.removeprefix("cv-")
            pdf = role_dir / f"cv-{language}.pdf"
            log = role_dir / f"cv-{language}.log"
            self.assertTrue(pdf.is_file(), f"Compile {pdf} before running this test")
            self.assertTrue(log.is_file(), f"Compile {source} before running this test")
            self.assertNotIn("Overfull", log.read_text(encoding="utf-8", errors="replace"), source)

            text = extract_pdf(pdf)
            pages = [page for page in text.split("\f") if page.strip()]
            self.assertGreaterEqual(len(pages), 1, pdf)
            if role_dir.name in ONE_PAGE_ROLES:
                self.assertEqual(len(pages), 1, pdf)

            lines = [normalized(line) for line in text.splitlines()]
            for date in date_entries(source):
                expected = normalized(date.replace("--", "-"))
                matching_lines = [line for line in lines if expected in line]
                self.assertTrue(matching_lines, f"{pdf}: missing date {date!r}")
                self.assertTrue(
                    any(line.split(expected, 1)[1].strip() for line in matching_lines),
                    f"{pdf}: date {date!r} is not on the same line as job content",
                )

    def test_warehouse_courier_wraps_under_the_job_text(self):
        pdf = ROOT / "roles" / "warehouse-master" / "cv-en.pdf"
        document = ET.fromstring(extract_pdf(pdf, layout=True))
        target_blocks = []
        for block in document.iter(f"{XHTML}block"):
            lines = list(block.findall(f"{XHTML}line"))
            texts = [
                " ".join((word.text or "") for word in line.findall(f"{XHTML}word"))
                for line in lines
            ]
            for index, text in enumerate(texts):
                if "Independent Courier" in text:
                    target_blocks.append((lines, texts, index))
        self.assertTrue(target_blocks, "Courier entry was not found in the warehouse PDF")

        lines, texts, index = target_blocks[0]
        self.assertLess(index + 1, len(lines), "Courier entry no longer wraps")
        first_line = lines[index]
        continuation = lines[index + 1]
        first_text = texts[index]
        self.assertIn("Apr 2025", first_text)
        title_word = next(
            word for word in first_line.findall(f"{XHTML}word")
            if word.text == "Independent"
        )
        title_x = float(title_word.attrib["xMin"])
        continuation_x = float(continuation.attrib["xMin"])
        self.assertLessEqual(abs(title_x - continuation_x), 2.0)


if __name__ == "__main__":
    unittest.main()
