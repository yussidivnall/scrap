import json
import re
import Har

TEST_CAPTURE_FILE = "./tests/test_data/forum.red.1.har"


def test_find():
    parser = Har.Parser(TEST_CAPTURE_FILE)
    matched = parser.find_entries(
        {"url_regex": "^https:\/\/www\.forums\.red.*"})
    urls = [e['request']['url'] for e in matched]
    print(urls)
    assert 'https://www.forums.red/images/flairs/down.png' in urls


def test_filter_out():
    parser = Har.Parser(TEST_CAPTURE_FILE)
    reject = [
        {"url_regex": "^.*\.(png|gif)$"},
        {"url_regex": "^.*\.(js|css)$"},
        {"url_regex": "^.*.styles.css.*$"},
        {"url_regex": 'https://manager.smartlook.com/rec/check'},
        {"mimetype_regex": 'text\/css'},
        {"mimetype_regex": 'image\/(png|jpeg)'},
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
        assert not re.match("^.*\.(png|gif)$", url)
        assert not re.match("image\/(png|jpeg)", content['mimeType'])
    # assert False


def test_filter_any():
    parser = Har.Parser(TEST_CAPTURE_FILE)
