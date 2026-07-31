from paperlib.models.paper import Paper
from paperlib.naming import filename_for

def test_filename():
    p=Paper(doi="10.1/x", title="A Digital Twin: Framework?", authors=["Guido Perboli"], journal_abbr="TRC", year=2024)
    assert filename_for(p)=="2024 - TRC - Perboli - A Digital Twin Framework.pdf"
