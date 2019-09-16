import Dom
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


def test_nesting():
    html = """
    <html>
        <body>
            <div class="comments">
                <div class="comment">
                I am very very very wrong about this!
                    <div class="comment">
                    No, you'ew right!!!
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

				</div>
            </div>
        </body>
    </html>
    """
    p = Dom.Parser(html)
    print(p)
    node_xpath = "//div[@class = 'comment']"
    nodes = p.root.xpath(node_xpath)
    extracted = {'nodes': []}  # extracted other keys (author,text,nodes,etc)
    root_nodes = [nodes[0]]
    depth = p.node_depth(nodes[0])
    for i in range(1, len(nodes)):
        n = nodes[i]
        d = p.node_depth(n)
        if d == depth:
            root_nodes.append(n)
        else:
            pass
            # extracted = {'nodes': []}  # extracted other keys (author,text,nodes,etc)
            # root_nodes[i-1]['nodes'].append(

    print(root_nodes)
    # for n in nodes:
    #     # print(etree.tostring(n))
    #     print(n)
    #     print(p.node_depth(n))
    #     print("-----")
    # print(nodes)
    assert False
