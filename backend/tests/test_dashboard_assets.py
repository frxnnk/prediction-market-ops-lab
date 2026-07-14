from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_dashboard_declares_an_existing_favicon() -> None:
    index = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")

    assert 'rel="icon"' in index
    assert 'href="/favicon.svg"' in index
    assert (ROOT / "dashboard" / "public" / "favicon.svg").is_file()
