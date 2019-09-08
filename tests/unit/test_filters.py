import pytest
TEST_FILE = "tests/test_data/forum.red.1.har"


def test_restrict_url_regexp():
    entry = {"request": {"url": "https://www.example.com/something.png"},
             "response": {}}
    restriction = {
        "url_regexp": "https://.*.png"
    }

    # assert HarParser.filter_entry(entry, restriction)
    restriction = {
        "url_regexp": "https://.*.html"
    }
    # assert not HarParser.filter_entry(entry, restriction)


def test_filter_har():
    restrictions = [
        {"url_regexp": "https://.*.png"}
    ]
    # matched = HarParser.filter_har(TEST_FILE, restrictions)
    # assert False
