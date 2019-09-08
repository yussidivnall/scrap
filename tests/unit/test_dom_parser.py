import Dom
import lxml


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
