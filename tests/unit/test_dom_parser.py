from car_scraper import Dom
import lxml
from lxml import etree


def test_extract():
    dom_text = """<html><body><div id="something">this</div></body></html>"""
    p = Dom.Parser(dom_text)

    interesting_parts = {
        'something': '//div[@id="something"]',
        'else': '//div/text()',
    }
    matched = p.extract(interesting_parts)
    assert len(matched['something']) == 1
    assert matched['else'] == ['this']
    assert type(matched['something'][0]) == lxml.etree._Element
    print(type(matched['something'][0]))
    print(matched)
    print()


def test_input_types():
    DOM_TEXT='<html><body></body></html>'
    XML_TEXT='<?xml version="1.0" encoding="utf-8" ?><timedtext format="3">'
    JSON_TEXT='{"key":{"value1":2, "value2":"hi"}}'
    DICT ={"key":{"value1":2, "value2":"hi"}}

    guess = Dom.Parser.text_type(DOM_TEXT)
    assert guess == "HTML"

    guess = Dom.Parser.text_type(XML_TEXT)
    assert guess == "XML"

    guess = Dom.Parser.text_type(JSON_TEXT)
    assert guess == "JSON"

    guess = Dom.Parser.text_type("Some words")
    assert guess == "OTHER"



nested_html = """
<html>
    <body>
        <div class="comments">
            <div class="comment">
            I am very very very wrong about this!
                <div class="comment">
                No, you're right!!!
                    <div class="comment">
                        Wrong1!!!
                    </div>
                    <div class="comment">
                        Wrong2!!!
                    </div>
                    <div class="comment">
                        Wrong3!!!
                    </div>
                </div>
            </div>
            <div class="comment">
            I am the root of the problem!
                <div class="comment">
                    Don't be so harsh on yourself, we all are!
                </div>
            </div>
        </div>
    </body>
</html>
"""

def test_nesting():
    p = Dom.Parser(nested_html)
    print(p)
    node_xpath = "//div[@class = 'comment']"
    nodes = p.root.xpath(node_xpath)
    extracted = {'nodes': []}  # extracted other keys (author,text,nodes,etc)
    root_nodes = [nodes[0]]
    depth = p.node_depth(nodes[0])
    for i in range(1, len(nodes)):
        n = nodes[i]
        d = p.node_depth(n)
        print(n, d)
        # if d == depth:
        #     root_nodes.append(n)
        # else:
        #     pass
            # extracted = {'nodes': []}  # extracted other keys (author,text,nodes,etc)
            # root_nodes[i-1]['nodes'].append(

    # print(root_nodes)
    # for n in nodes:
    #     # print(etree.tostring(n))
    #     print(n)
    #     print(p.node_depth(n))
    #     print("-----")
    # print(nodes)
    # assert False

def test_get_nesting():
    p = Dom.Parser(nested_html)
    print(p)
    node_xpath = "//div[@class = 'comment']"
    nodes = p.get_nesting(node_xpath) # a list of [( <XML NODE> , depth), ...]
    for n in nodes:
        elem = n[0] 
        depth = n[1]
        print("{}   {}".format(depth, elem.text.strip()))
        print(type(elem))
    print(nodes)
    assert nodes[0][1] == 4
    assert nodes[1][1] == 5
    assert nodes[2][1] == 6
    assert nodes[3][1] == 6
    assert nodes[4][1] == 6
    assert nodes[5][1] == 4
    assert nodes[6][1] == 5
    assert "I am very very very wrong " in nodes[0][0].text
    assert "you're right" in nodes[1][0].text
    assert len(nodes) == 7


from lxml import etree # noqa
def test_xml_with_encoding():
    XML_TEXT='''<?xml version="1.0" encoding="utf-8" ?>
    <timedtextformat="3">
        <taggy>
            <mctagface>
                Hi
            </mctagface>
        </taggy>
    </timedtextformat>'''
    #p = Dom.Parser(XML_TEXT)
    xml = etree.XML(XML_TEXT)
