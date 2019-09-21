from lxml import etree
import Har
import Dom
TEST_CAPTURE_FILE = "./tests/test_data/forum.red.1.har"

def test_trp():
    har_parser = Har.Parser(TEST_CAPTURE_FILE)
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
        print(url)
        cont = dom_parser.extract({
                "content":  "//div[@class='container']",
                "comments": "//div[contains(@class,'commentbody')]//p//text()",
                "comment_bodies": "//div[contains(@class,'commentbody')]",
                "authors":
                "//div[@class='comments']//a[starts-with(@href,'{}')]/text()".format(
                    user_page_base_url)

            })
        # print(dom_parser.prettify())
        # dom_parser.prettify()
        print("=============")

    # assert False

def test_trp_nesting():
    har_parser = Har.Parser(TEST_CAPTURE_FILE)
    # E.G
    # https://www.forums.red/p/TheRedPill/220590/spain_gender_laws_a_country_against_men_the_woman_decides_to
    story_page_restriction = {
        "url_regex": "^.*.\/p\/[a-zA-Z0-9_-]*/[0-9]*/[a-zA-Z0-9_-]*$"
    }

    # Container of comment node
    # comments_xpath="//div[contains(@class,'commentbody')]"
    comments_xpath="//div[contains(@class,'therest')]"


    # https://www.forums.red/u
    user_page_base_url = "https://www.forums.red/u/"
    pages = har_parser.find_entries(story_page_restriction)
    for p in pages:
        url = p['request']['url']
        txt = p['response']['content']['text']
        print(url)
        dom_parser = Dom.Parser(txt)
        comments = dom_parser.get_nesting(comments_xpath)

    print("Page")
    dom_parser = Dom.Parser(pages[2]['response']['content']['text'])
    # print(etree.tostring(page_0.root, pretty_print=True).decode())
    comments = dom_parser.get_nesting(comments_xpath)
    for c in comments:
        elem = c[0]
        depth = c[1]
        node_parser = Dom.Parser(elem)
        node_parser.root = elem
        extract_template = {
            # "author": "span[@class='commentdetails']/a[@class='']",
            "author": "span[@class='commentdetails']/a[contains(@href,'https://www.forums.red/u/')]",
            "score": "span[@class='commentdetails']/span[@class='scores']",
            "time": "span[@class='commentdetails']/span[@class='timeposted']",
            "text": "div[contains(@class,'commentbody')]/p",
                # "comments": "//div[contains(@class,'commentbody')]//p//text()",
        }
        extracted = node_parser.extract(extract_template)
        print(extracted)
        print(extracted['time'][0].text)
        if extracted['author']:
            print(extracted['author'][0].text)
            print(extracted['score'][0].text)
            txt = [etree.tostring(p) for p in extracted['text']]
            print(txt)
        else:
            print('deleted')
        print("===")
        # print(etree.tostring(c[0]))
        # txt = "".join(c[0].itertext())
        # comment_id = c[0].attrib["id"]
        # print(comment_id)
        # print(c[1], txt)
    # print(comments)
    # print(pages[0]['response']['content']['text'])
    # assert False


def print_comment(c):
    """Helper to print a comment dict """
    if not c['author']:
        print("[Deleted]\n")
        return
    print("{}> {}, {}, {}".format(
            c['nesting_level'],
            c['author'][0].text,
            c['score'][0].text,
            c['time'][0].text
        )
    )
    comment_text = " ".join(["".join(n.itertext()) for n in c['text']])
    print(comment_text)
    print()

def test_trp_extract_nested():
    har_parser = Har.Parser(TEST_CAPTURE_FILE)
    # Restrict to story URLs E.G
    # https://www.forums.red/p/TheRedPill/220590/spain_gender_laws_a_country_against_men_the_woman_decides_to
    story_page_restriction = {
        "url_regex": "^.*.\/p\/[a-zA-Z0-9_-]*/[0-9]*/[a-zA-Z0-9_-]*$"
    }

    # Container of comment node
    comment_container_xpath = "//div[contains(@class,'therest')]"
    extract_template = {
        "author": "span[@class='commentdetails']/a[contains(@href,'https://www.forums.red/u/')]",
        "score": "span[@class='commentdetails']/span[@class='scores']",
        "time": "span[@class='commentdetails']/span[@class='timeposted']",
        "text": "div[contains(@class,'commentbody')]/p",
    }
    pages = har_parser.find_entries(story_page_restriction)
    for p in pages:
        url = p['request']['url']
        txt = p['response']['content']['text']
        print(url)
        print("==========================")
        dom_parser = Dom.Parser(txt)
        comments = dom_parser.extract_nested(
            comment_container_xpath,
            extract_template
            )
        for c in comments:
            print_comment(c)
    assert False
