"""One-off driver: resolve every (class, display_name) pair in
Scrapers/subclasses2014.txt against dnd5e.wikidot.com's discovered subclass
pages (see discover_all_subclasses() in WikiDotSubclassScraper2014.py), fetch
every match, and write it to SourceTexts/SubclassTexts2014/.

Usage: python Scrapers/FetchSubclassRoster2014.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from WikiDotSubclassScraper2014 import (
    OUTPUT_DIR,
    SubclassParser,
    discover_all_subclasses,
    fetch_subclass,
    resolve_subclass_page_ref,
    slug_to_filename,
)

ROSTER_PATH = Path(__file__).resolve().parent / "subclasses2014.txt"


def parse_roster(path: Path) -> list[tuple[str, str]]:
    """Parse the '### ClassName' / '* Display Name' roster format into a flat
    list of (class_name_lower, display_name) pairs."""
    entries: list[tuple[str, str]] = []
    current_class: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("### "):
            current_class = line[4:].strip().lower()
        elif line.startswith("* ") and current_class:
            display_name = line[2:].strip()
            entries.append((current_class, display_name))
    return entries


if __name__ == "__main__":
    roster = parse_roster(ROSTER_PATH)
    print(f"Parsed {len(roster)} requested subclasses from {ROSTER_PATH}")

    print("Discovering official subclasses per class from dnd5e.wikidot.com...")
    discovered = discover_all_subclasses()
    for class_name, entries in discovered.items():
        print(f"  {class_name}: {len(entries)} discovered")

    # Resolve each requested (class, display_name) -> page_ref.
    resolved: dict[tuple[str, str], str] = {}
    unresolved: list[tuple[str, str]] = []
    for class_name, display_name in roster:
        page_ref = resolve_subclass_page_ref(
            class_name, display_name, discovered.get(class_name, [])
        )
        if page_ref is None:
            unresolved.append((class_name, display_name))
        else:
            resolved[(class_name, display_name)] = page_ref

    print(f"Resolved {len(resolved)}/{len(roster)}; unresolved: {len(unresolved)}")
    if unresolved:
        for class_name, display_name in unresolved:
            print(f"  UNRESOLVED [{class_name}] {display_name!r}")

    # Fetch every distinct resolved page_ref (a couple of requested entries
    # could in principle resolve to the same page_ref).
    page_refs = sorted(set(resolved.values()))

    results: dict[str, SubclassParser] = {}
    fetch_failed: list[str] = []

    MAX_WORKERS = 4
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_subclass, page): page for page in page_refs}
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Fetching subclasses"
        ):
            page_ref = futures[future]
            try:
                _, parser = future.result()
                results[page_ref] = parser
            except Exception as e:
                print(f"  FAILED {page_ref}: {e}")
                fetch_failed.append(page_ref)

    # slug_to_filename() drops the class prefix (e.g. "barbarian:wild-magic" and
    # "sorcerer:wild-magic" both -> "wild_magic.txt"); disambiguate any such
    # collisions with a "{class}_{slug}.txt" name instead, leaving every other
    # (non-colliding) file on the normal bare-slug convention.
    filenames: dict[str, list[str]] = {}
    for page_ref in results:
        filenames.setdefault(slug_to_filename(page_ref), []).append(page_ref)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for page_ref, parser in results.items():
        fname = slug_to_filename(page_ref)
        if len(filenames[fname]) > 1:
            class_name, slug = page_ref.split(":", 1)
            fname = f"{class_name}_{slug.replace('-', '_')}.txt"
            print(f"  NOTE: disambiguating filename collision -> {fname}")
        out_path = OUTPUT_DIR / fname
        parser.write_to_path(out_path)
        print(f"Wrote {page_ref} -> {out_path}")

    print()
    print(f"Requested: {len(roster)}")
    print(f"Resolved: {len(resolved)}")
    print(f"Fetched+written: {len(results)}")
    print(f"Fetch failures ({len(fetch_failed)}): {', '.join(fetch_failed)}")
    if unresolved:
        print(f"Unresolved ({len(unresolved)}):")
        for class_name, display_name in unresolved:
            print(f"  [{class_name}] {display_name}")
