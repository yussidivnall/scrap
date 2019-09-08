import re


class Restriction():
    restriction = {
        'url_regexp': None,
        'mimetype_regex': None,
        'content_type': None,
        'content_regex': None,
    }

    def __init__(self, restriction):
        """ Set the filter's restriction

        Arguments:
            restriction: a dictionary
                url_regexp: a regular expression to compare to url
                mime_regexp:
                    a regular expression to compare to
                    entry['response']['content']['mimeType']

                content_type: not implemented
                content_regex: not implemented
                ...
        """
        self.restriction = restriction

    def match_entry(self, entry):
        """ Returns True if all (not None) har entry 
        restrictions are fulfiled
        Currently only url_regex is tested

        Arguments:
            entry: a request/response entry from a har
        Returns:
            True is all restrictions on entry match
        """

        url = entry['request']['url']
        content = entry['response']['content']

        url_regex = self.restriction.get('url_regex', None)
        mimetype_regex = self.restriction.get('mimetype_regex', None)

        if url_regex:
            match = re.match(url_regex, url)
            if not match:
                return False
        if mimetype_regex and content:
            mimetype = content['mimeType']
            match = re.match(mimetype_regex, mimetype)
            if not match:
                return False
        return True
