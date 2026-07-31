from paperlib.utils.doi import normalize_doi

def test_normalize():
    assert normalize_doi("https://doi.org/10.1000/XYZ.1") == "10.1000/xyz.1"
