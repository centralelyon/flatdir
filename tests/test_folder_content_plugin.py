from pathlib import Path

from flatdir.plugins.folder_content import has_ext, has_postfix


def test_folder_content_has_postfix(tmp_path: Path):
    # Setup test directory structure
    root = tmp_path
    toto = root / "toto"
    toto.mkdir()
    
    # Matching files with postfix
    (toto / "toto_tata.json").touch()
    (toto / "toto_tutu.xml").touch()
    
    # File without postfix (should be ignored for has_postfix)
    (toto / "toto.txt").touch()
    
    # Non-matching files (should be ignored)
    (toto / "other_tata.json").touch()
    (toto / "tototata.json").touch()
    
    # Not a file (should be ignored)
    sub = toto / "toto_sub"
    sub.mkdir()

    # File is ignored, returns None
    assert has_postfix((toto / "toto_tata.json"), root) is None

    # Directory returns matching postfixes
    assert has_postfix(toto, root) == ["tata", "tutu"]


def test_folder_content_has_ext(tmp_path: Path):
    # Setup test directory structure
    root = tmp_path
    toto = root / "toto"
    toto.mkdir()
    
    # Matching files (exact name + extensions)
    (toto / "toto.json").touch()
    (toto / "toto_tata.xml").touch()
    (toto / "toto_tutu.csv").touch()
    
    # No extension
    (toto / "toto").touch()
    (toto / "toto_noext").touch()
    
    # Non-matching file names
    (toto / "other.txt").touch()

    # File is ignored, returns None
    assert has_ext((toto / "toto.json"), root) is None

    # Directory returns matching extensions
    assert has_ext(toto, root) == ["csv", "json", "xml"]
