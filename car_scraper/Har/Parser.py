import json
from car_scraper import Har
import copy
# from Har import Restriction


class Parser():
    def __init__(self, har_file_name=None, har_file_contents=None):
        """ init parser

        Arguments:
            har_file_name:
                initilise using a filename OR
            har_file_contents:
                initilise using the contents of an already open HAR file
        """
        if har_file_name:
            with open(har_file_name, "r") as fp:
                self.har_file = json.load(fp)
            self.entries = self.har_file['log']['entries']
        elif har_file_contents:
            self.har_file = json.load(har_file_contents)
            self.entries = self.har_file['log']['entries']
        else:
            raise ValueError(
                "Required at least a har_file_name or a har_file_contents"
                )

    def find_entries(self, restriction):
        """ Return a list of entries which fulfill restriction

        Arguments:
            restriction: a restriction dicitonary
        Returns:
            a list of matching entries
        """
        rest = Har.Restriction(restriction)
        ret = filter(lambda x: rest.match_entry(x), self.entries)
        return list(ret)

    def filter_out(self, reject):
        """ Iteratively reject all entries matching reject

        Arguments:
            reject: a list of restrictions
        """
        matched = copy.copy(self.entries)
        for r in reject:
            rest = Har.Restriction(r)
            matched = list(
                filter(lambda x: not rest.match_entry(x),
                       matched
                       )
            )
        return matched

    def filter_any(self, restrictions):
        """ Return entries which match any of the restrictions

        The restriction needs to be fully matching, but only one
        restriction needs to fully match in order to match the entry
        """
        ret = []
        for r in restrictions:
            ret.extend(self.find_entries(r))
        return ret
        # return list(set(ret))
