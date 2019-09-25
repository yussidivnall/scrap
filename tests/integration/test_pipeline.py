from lxml.etree import XMLSyntaxError
from lxml import etree
import re
from car_scraper import Har, Dom

TEST_CAPTURE_FILE = "./tests/test_data/forum.red.1.har"


def test_trp_forum_har():
    har_parser = Har.Parser(TEST_CAPTURE_FILE)
    reject_entries = [
        {"url_regex": "^.*\.(png|gif)$"},
        {"url_regex": "^.*\.(js|css)$"},
        {"url_regex": "^.*.styles.css.*$"},
        {"url_regex": 'https://manager.smartlook.com/rec/check'},
        {"url_regex": '^.*./postback\.php\?updateicons=[0-9]\&lc=[0-9]'},
        {"url_regex": '^.*.\/scripts\/scripts\.js\?version=[0-9]{1,10}'},
        {"mimetype_regex": 'text\/css'},
        {"mimetype_regex": 'image\/(png|jpeg)'},
    ]
    matched = har_parser.filter_out(reject_entries)
    accept_entries = [
        {"url_regex": "^.*.\/i\/$"},  # Homepage
        {"url_regex": "^.*.\/u\/[a-zA-Z0-9_-]*$"},  # User Homepage
        {"url_regex": "^.*.\/p\/[a-zA-Z0-9_-]/[0-9]*/[a-zA-Z0-9_-]*$"},
        {
            "url_regex":
            "^ .*.\/statuses.php\?userid=CainPrice\&absdefasdf=1\&start=10"
        },
        {
            "url_regex":
            "^.*.\/i\/TheRedPill\/\?start=15\&wrap=false&timeframe=1\&userid=\&sort=3"
        },

    ]
    # https://www.forums.red/statuses.php?userid=CainPrice&absdefasdf=1&start=10
    # https://www.forums.red/i/TheRedPill/?start=15&wrap=false&timeframe=1&userid=&sort=3

    print(len(matched))

    # E.G
    # https://www.forums.red/p/TheRedPill/220590/spain_gender_laws_a_country_against_men_the_woman_decides_to
    story_page_restriction = {
        "url_regex": "^.*.\/p\/[a-zA-Z0-9_-]*/[0-9]*/[a-zA-Z0-9_-]*$"
    }
    # https://www.forums.red/u://www.forums.red/u/
    user_page_base_url = "https://www.forums.red/u/"
    pages = har_parser.find_entries(story_page_restriction)
    for p in pages:
        url = p['request']['url']
        txt = p['response']['content']['text']
        dom_parser = Dom.Parser(txt)
        cont = dom_parser.extract(
            {
                "content":  "//div[@class='container']",
                "comments": "//div[contains(@class,'commentbody')]//p//text()",
                "comment_bodies": "//div[contains(@class,'commentbody')]",
                "authors":
                "//div[@class='comments']//a[starts-with(@href,'{}')]/text()".format(
                    user_page_base_url)

            })
        assert len(cont) == 4
        # assert len(cont['comments']) == len(cont['authors'])
        assert len(cont['content']) == 1
        print(url)
        # print(cont['comments'])
        print(cont['comment_bodies'])
        for bod in cont['comment_bodies']:
            print(etree.tostring(bod))
        # print(len(cont['comments']))
        print(cont['authors'])
        print()

        # for comment in cont['comments']:
        #     print(comment)
        #     print("---")
        # # print("content: {}".format(cont['content'].tostring()))
        # print(cont['as'])
        # for a in cont['as']:
        #     print(a)
        # # print(etree.tostring(comment, pretty_print=True))

        # print(len(cont['comments']))
        # print(cont)
        # print(cont.keys())
        # print(url)
        # print(etree.tostring(cont['comments'], pretty_print=True))
    # assert False
