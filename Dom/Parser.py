from lxml import etree


class Parser():
    """ Helpers for parsing DOM document """

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


    def get_nesting(self,  node_xpath):
        """ Return an ordered list of nodes matching xpath expression and their
        respective nesting level

        Arguments:
            node_xpath: an xpath expression to find the comment containing tag
        Returns: A list of node, node_depth pairs.
        """
        ret = []
        nodes = self.root.xpath(node_xpath)
        extracted = {'nodes': []}  # extracted other keys (author,text,nodes,etc)
        for i in range(0, len(nodes)):
            n = nodes[i]
            d = self.node_depth(n)
            ret.append( (n,d) )
        return ret


    def nesting(self, node_list, expresisons):
        #@DEPRECATED NOT WORKING
        """ Construct a discussion thread like object from
        nested html elements.
        Recuse over matched
        Arguments:
            node_list: a list of matched nodes (from previous recursion)
            expressions: a dictionary with 'keys:xpath_expressions',
            with one of the keys being "nodes": and an xpath to match nodes for
            next recursion.
        Returns:
            a dictionary with populated keys as in 'expressions'. and one key
            "nodes": containing a list of matching nodes, will iterate over
            those with the next recursion

        """
        ret = {}
        for node in node_list:
            for key in expresisons.keys():
                xpath = expresisons[key]
                ret[key] = node.xpath(xpath)
        pass

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
