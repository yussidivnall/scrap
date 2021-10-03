import logging
import json
# from json import JSONDecodeError
from lxml import etree
# from lxml.etree import XMLSyntaxError
from dicttoxml import dicttoxml


class Parser():
    """ Helpers for parsing DOM document """

    @staticmethod
    def text_type(txt):
        """ Determine the type of a string
        Try to guess if JSON, HTML, or other
        Argument:
            txt: Some text
        Returns:
            "HTML", "JSON", "XML" or "OTHER"
        """
        if isinstance(txt, bytes):
            txt = str(txt)
        if txt.startswith('{'):
            return "JSON"
        if txt.startswith('['):
            return "JSON"
        if txt.startswith('<!DOCTYPE html'):
            return "HTML"
        if txt.startswith('<?xml version="1.0"'):
            return "XML"
        if '<html' in txt:
            return "HTML"
        return "OTHER"

    def __init__(self, dom):
        if isinstance(dom, str) or isinstance(dom, bytes):
            TYPE = self.text_type(dom)
            if TYPE == "JSON":
                dom_dict = json.loads(dom)
                self.dom_text = str(dicttoxml(dom_dict))
                self.root = etree.HTML(self.dom_text)
            elif TYPE == "HTML":
                print("HTML INPUT")
                self.dom_text = dom
                self.root = etree.HTML(str(dom))
            elif TYPE == 'XML':
                print("XML INPUT")
                self.dom_text = dom
                self.root = etree.fromstring(dom)
            else:
                raise RuntimeError("Unknown input: {}".format(dom[0:100]))
        elif isinstance(dom, etree._Element):
            self.root = dom
            self.dom_text = etree.tostring(dom)
        elif isinstance(dom, dict):
            self.dom_text = str(dicttoxml(dom))
            self.root = etree.HTML(self.dom_text)
        elif isinstance(dom, list):
            logging.warning("Response content is a list")
            self.dom_text = str(dicttoxml(dom))
            self.root = etree.HTML(self.dom_text)
        else:
            raise TypeError("Unknown DOM element type {}".format(type(dom)))
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

    def get_nesting(self,  node_xpath):
        """ Return an ordered list of nodes matching xpath expression and their
        respective nesting level

        Arguments:
            node_xpath: an xpath expression to find the comment containing tag
        Returns: A list of node, node_depth pairs.
        """
        ret = []
        nodes = self.root.xpath(node_xpath)
        # extracted other keys (author,text,nodes,etc)
        # extracted = {'nodes': []}
        for i in range(0, len(nodes)):
            n = nodes[i]
            d = self.node_depth(n)
            ret.append((n, d))
        return ret

    def extract_nested(self, container_xpath, expresisons):
        """  extract from nested DOM elements

        Arguments:
            container_xpath: An xpath expression to match the nested DOM
            elements, e.g. "//div[@class='comment_container']"

            expressions: a dictionary with 'keys:xpath_expressions', to extract
            data from each matching container_xpath. note that top level DOM
            nodes contain their nested decendents.
            e.g.
                {
                    "author": "div[@class='comment_author']",
                    "text": "div[@class='comment_text']/p",
                }
        Returns:
            an ordered list of dictionaries with populated data from
            "expressions" and for each node nesting level
            e.g.
            [
             {"nesting_level":6, "author":[<Element>], "text":[<Element>,...]},
             {"nesting_level":9, "author":[<Element>], "text":[<Element>,...]},
             {"nesting_level":9, "author":[<Element>], "text":[<Element>]},
             ...
            ]
        """
        ret = []
        comment_nodes = self.get_nesting(container_xpath)
        for node, depth in comment_nodes:
            parser = Parser(node)
            element = parser.extract(expresisons)
            element['nesting_level'] = depth
            ret.append(element)
        return ret

    @staticmethod
    def node_depth(node):
        """ Return a node's depth
        """
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d

    def prettify(self):
        """
        """
        print(etree.tostring(self.root, method='html',
                             encoding='unicode', pretty_print=True))
