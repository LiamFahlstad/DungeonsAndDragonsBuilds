import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from WikiDotPageRenderer import render_content_lines

BASE_URL = "https://dnd2024.wikidot.com/"


class ClassNotFoundError(Exception):
    """Raised when the class main page does not exist on dnd2024.wikidot.com."""

    pass


class ClassParser:
    def __init__(self, page_ref: str):
        """page_ref is e.g. 'paladin:main' (class:main)."""
        self.page_ref = page_ref
        self.url = f"{BASE_URL}{page_ref}"
        self.soup = None
        self.content = None
        self.title_div = None
        self.breadcrumbs_div = None

    def fetch(self):
        """Download the class main page HTML and prepare the soup object."""
        response = requests.get(self.url)

        self.soup = BeautifulSoup(response.text, "html.parser")
        self.content = self.soup.find("div", id="page-content")

        if not self.content:
            raise ValueError(
                f"Could not find main page content for '{self.page_ref}' ({self.url})."
            )

        not_found = self.content.find("p", id="404-message")
        if response.status_code != 200 or not_found:
            raise ClassNotFoundError(
                f"Class page '{self.page_ref}' ({self.url}) does not exist "
                f"(HTTP {response.status_code})."
            )

        self.title_div = self.soup.find("div", class_="page-title")
        self.breadcrumbs_div = self.soup.find("div", class_="breadcrumbs")

    # -------------------
    # Rendering
    # -------------------

    def get_lines(self) -> list[str]:
        """Render the page into the exact plain-text line list: page title, breadcrumbs,
        then the rendered #page-content blocks (no blank line separating any of these).
        """
        lines: list[str] = []

        if self.title_div:
            lines.append(self.title_div.get_text().strip())
        if self.breadcrumbs_div:
            lines.append(self.breadcrumbs_div.get_text().strip())

        lines.extend(render_content_lines(self.content))

        return lines

    def get_text(self) -> str:
        return "\n".join(self.get_lines())

    # -------------------
    # to_dict / print_info / write_to_file trio
    # -------------------

    def to_dict(self) -> dict:
        return {
            "page_ref": self.page_ref,
            "url": self.url,
            "text": self.get_text(),
        }

    def print_info(self):
        data = self.to_dict()
        print(data["text"])

    def write_to_file(self, file):
        """Write the rendered class text to an already-open file handle."""
        file.write(self.get_text())
        file.write("\n")

    def write_to_path(self, path: Path):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            self.write_to_file(f)


def slug_to_filename(page_ref: str) -> str:
    """'paladin:main' -> 'paladin.txt'. (Every class page's slug is literally 'main', so
    we key the filename off the category instead of the slug.)
    """
    category = page_ref.split(":", 1)[0]
    return category.replace("-", "_") + ".txt"


def fetch_class(page_ref: str, max_retries: int = 3) -> tuple[str, ClassParser]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            parser = ClassParser(page_ref)
            parser.fetch()
            return page_ref, parser
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_class({page_ref!r}) failed")


DEFAULT_PAGES = [
    "paladin:main",
    "ranger:main",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "SubclassTexts"


if __name__ == "__main__":
    pages = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_PAGES

    results: dict[str, ClassParser] = {}
    failed: list[str] = []

    MAX_WORKERS = 4

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_class, page): page for page in pages}

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching classes",
        ):
            page_ref = futures[future]
            try:
                _, parser = future.result()
                results[page_ref] = parser
            except Exception as e:
                print(f"  FAILED {page_ref}: {e}")
                failed.append(page_ref)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for page_ref, parser in results.items():
        out_path = OUTPUT_DIR / slug_to_filename(page_ref)
        parser.write_to_path(out_path)
        print(f"Wrote {page_ref} -> {out_path}")

    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
