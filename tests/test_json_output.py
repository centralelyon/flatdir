import json

from flatdir import listing


def test_outputs_valid_json(tmp_path):

    # create a small directory with one file
    sub = tmp_path / "sub"
    sub.mkdir()
    f = sub / "a.txt"
    f.write_text("this is a test")

    entries = listing.list_entries(tmp_path)

    # write and read JSON
    text = json.dumps(entries)
    data = json.loads(text)

    # ensure our file is present in the listing
    assert any(entry.get("name", "").endswith("a.txt") for entry in data)
