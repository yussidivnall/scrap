from lxml import etree


class Parser():

    def __init__(self, dom_text):
        self.dom_text = dom_text
        self.root = etree.HTML(dom_text)
        # self.root = etree.XML(dom_text)

    def extract(self, expressions):
        """ Populate a dictionary with xpath extracted data

        Aruments:
            expressions: A dictionary of "key:xpath_expression"

        Returns:
            a dictionary of "key":"xpath_matched"
        """
        ret = {}
        for key in expressions.keys():
            expression = expressions[key]
            matched = self.root.xpath(expression)
            ret[key] = matched
        return ret

    def prettify(self):
        """
        """
        print(etree.tostring(self.root, method='html',
                             encoding='unicode', pretty_print=True))
