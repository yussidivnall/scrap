import re
from car_scraper import Har

TEST_CAPTURE_FILE = "./tests/test_data/forum.red.1.har"


def test_open_har_file_type():
    # Test opening as file instead a path string
    with open(TEST_CAPTURE_FILE) as fp:
        parser = Har.Parser(har_file_contents=fp)
        print(parser)
        assert type(parser) == Har.Parser
        matched = parser.find_entries(
            {"url_regex": r"^https:\/\/www\.forums\.red.*"})
        urls = [e['request']['url'] for e in matched]
        print(urls)
        assert 'https://www.forums.red/images/flairs/down.png' in urls


def test_find():
    parser = Har.Parser(TEST_CAPTURE_FILE)
    matched = parser.find_entries(
        {"url_regex": r"^https:\/\/www\.forums\.red.*"})
    urls = [e['request']['url'] for e in matched]
    print(urls)
    assert 'https://www.forums.red/images/flairs/down.png' in urls


def test_filter_out():
    parser = Har.Parser(TEST_CAPTURE_FILE)
    reject = [
        {"url_regex": r"^.*\.(png|gif)$"},
        {"url_regex": r"^.*\.(js|css)$"},
        {"url_regex": r"^.*.styles.css.*$"},
        {"url_regex": r'https://manager.smartlook.com/rec/check'},
        {"mimetype_regex": r'text\/css'},
        {"mimetype_regex": r'image\/(png|jpeg)'},
    ]
    matched = parser.filter_out(reject)
    urls = [e['request']['url'] for e in matched]
    print(urls)
    for m in matched:
        url = m['request']['url']
        content = m['response']['content']
        print(url)
        # print(content.keys())
        # print("{}\n\n{}\n-----------".format(url, content))
        assert not re.match(r"^.*\.(png|gif)$", url)
        assert not re.match(r"image\/(png|jpeg)", content['mimeType'])
    # assert False


def test_filter_any():
    parser = Har.Parser(TEST_CAPTURE_FILE)
    accept = [
        {"url_regex": r"^.*\.(png|gif)$"},
        {"url_regex": r"^.*\.(js|css)$"},
    ]
    matched = parser.filter_any(accept)
    for m in matched:
        url = m['request']['url']
        print(url)
        assert re.match(r"^.*.\.(png|gif|js|css)$", url)

    # assert False
