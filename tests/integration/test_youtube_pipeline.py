import json
from lxml import etree
from dicttoxml import dicttoxml
from car_scraper import Har, Dom
TEST_CAPTURE_FILE = "./tests/test_data/youtube.com.1.har"

def test_get_json_response_content():
    """ Try and construct a Json Parser from JSON response contents
    """
    get_comments_url =\
        "^https:\/\/www\.youtube\.com\/comment_service_ajax\?action_get_comments.*"

    comment_container_xpath = "//comment"
    #commentRenderer
    extract_template = {
        "comment_id": "commentrenderer/commentid[1]/text()",
        "video_id": "commentrenderer/publishedtimetext//videoid[1]/text()",
        "text": "commentrenderer/contenttext/runs//text()",
        "author": "commentrenderer/authortext/simpletext/text()",
        "votes": "commentrenderer/votecount/simpletext//text()",
        "likes": "commentrenderer/likecount//text()",
        "replies": "commentrenderer/replycount//text()",
        "time": "commentrenderer/publishedtimetext[1]//text/text()",
    }
    har_parser = Har.Parser(TEST_CAPTURE_FILE)
    comment_entries = har_parser.find_entries(
        {"url_regex": get_comments_url}
        )
    for entry in comment_entries:
        url = entry['request']['url']
        txt = entry['response']['content']['text']
        print(url)
        # xml_text = str(dicttoxml(json.loads(txt), attr_type=False))
        # print(xml_text)
        # dom_parser = Dom.Parser(xml_text)
        dom_parser = Dom.Parser(json.loads(txt))
        comments = dom_parser.extract_nested(
            comment_container_xpath,
            extract_template
            )
        for c in comments:
            print(c)
            print(c['time'])
            print()

    # assert False
