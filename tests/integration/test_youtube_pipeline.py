import json
from car_scraper import Har, Dom
TEST_CAPTURE_FILE = "./tests/test_data/youtube.com.1.har"


def dtest_get_json_response_content():
    """ Try and construct a Json Parser from JSON response contents
    """
    get_comments_url =\
        r"^https:\/\/www\.youtube\.com\/comment_service_ajax\?action_get_comments.*"  # noqa

    comment_container_xpath = "//comment"
    # commentRenderer
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


def test_get_replies():

    harp = Har.Parser(TEST_CAPTURE_FILE)
    reply_url =\
        r"^https:\/\/www\.youtube\.com\/comment_service_ajax\?action_get_comment_replies.*"  # noqa
    reply_entries = harp.find_entries({"url_regex": reply_url})
    for entry in reply_entries:
        url = entry['request']['url']
        txt = entry['response']['content']['text']
        print(url)
        domp = Dom.Parser(txt)
        # replies = domp.extract({'txt':'//commentrenderer//text//text()'})
        # print(replies)
        comment_container_xpath = "//commentrenderer"
        extract_template = {
            "comment_id": "commentid[1]/text()",
            "video_id": "publishedtimetext//videoid[1]/text()",
            "text": "contenttext/runs//text()",
            "author": "authortext/simpletext/text()",
            "votes": "votecount/simpletext//text()",
            "likes": "likecount//text()",
            "replies": "replycount//text()",
            "time": "publishedtimetext[1]//text/text()",
            }
        replies = domp.extract_nested(
            comment_container_xpath, extract_template)
        print(replies)
    # assert False
