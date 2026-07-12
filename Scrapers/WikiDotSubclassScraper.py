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

# NOTE: A site-wide list of every subclass page can be discovered via
# https://dnd2024.wikidot.com/system:page-tags/tag/subclass
# (look for <div id="tagged-pages-list"> with
# <div class="pages-list-item"><div class="title"><a href="/{class}:{slug}">Name</a></div></div>).
# That full-site discovery/"--all" mode is intentionally not implemented here.


class SubclassNotFoundError(Exception):
    """Raised when the subclass page does not exist on dnd2024.wikidot.com."""

    pass


class SubclassParser:
    def __init__(self, page_ref: str):
        """page_ref is e.g. 'ranger:hollow-warden' (class:slug)."""
        self.page_ref = page_ref
        self.url = f"{BASE_URL}{page_ref}"
        self.soup = None
        self.content = None

    def fetch(self):
        """Download the subclass page HTML and prepare the soup object."""
        response = requests.get(self.url)

        self.soup = BeautifulSoup(response.text, "html.parser")
        self.content = self.soup.find("div", id="page-content")

        if not self.content:
            raise ValueError(
                f"Could not find main page content for '{self.page_ref}' ({self.url})."
            )

        not_found = self.content.find("p", id="404-message")
        if response.status_code != 200 or not_found:
            raise SubclassNotFoundError(
                f"Subclass '{self.page_ref}' ({self.url}) does not exist "
                f"(HTTP {response.status_code})."
            )

    # -------------------
    # Rendering
    # -------------------

    def get_lines(self) -> list[str]:
        """Render the page content into the exact plain-text line list."""
        return render_content_lines(self.content)

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
        """Write the rendered subclass text to an already-open file handle."""
        file.write(self.get_text())
        file.write("\n")

    def write_to_path(self, path: Path):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            self.write_to_file(f)


def slug_to_filename(page_ref: str) -> str:
    """'ranger:hollow-warden' -> 'hollow_warden.txt'."""
    slug = page_ref.split(":", 1)[-1]
    return slug.replace("-", "_") + ".txt"


def fetch_subclass(page_ref: str, max_retries: int = 3) -> tuple[str, SubclassParser]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            parser = SubclassParser(page_ref)
            parser.fetch()
            return page_ref, parser
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_subclass({page_ref!r}) failed")


DEFAULT_PAGES = [
    "paladin:oath-of-the-ancients",
    "ranger:hollow-warden",
    "ranger:winter-walker",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "SourceTexts" / "SubclassTexts"


if __name__ == "__main__":
    pages = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_PAGES

    results: dict[str, SubclassParser] = {}
    failed: list[str] = []

    MAX_WORKERS = 4

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_subclass, page): page for page in pages}

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching subclasses",
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
