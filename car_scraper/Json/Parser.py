
import logging
import csv
import json
import ijson
import jsonpath_rw
# from jsonpath_rw import jsonpath, parse

class Parser():

    def __init__(self, json_file,
                 prefix='item', template=None,
                 restrictions=[], postprocess_template = None
                 ):
        self.input_file = open(json_file, 'rb')
        self.prefix = prefix
        self.items = None # Items in input list
        self.entries = None # processed items (after template and restrictions)
        self.template = template
        self.restrictions=restrictions
        self.postprocess_template = postprocess_template

    # def __iter__(self):
    #     return self

    def __enter__(self):
        # Raw input item
        self.items = ijson.items(self.input_file, self.prefix)
        # Processed (templated) and restricted entries
        self.entries = self.entry_generator()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.input_file.close()

    def entry_generator(self):
        for item in ijson.items(self.input_file, self.prefix):
            entry = self.extract(item, self.template)
            if self.restricted(entry, self.restrictions):
                continue
            if self.postprocess_template:
                entry = self.postprocess(entry, self.postprocess_template)
            else:
                yield entry

    @staticmethod
    def postprocess(entry, postprocess_template):
        """ postprocess the entry based on a dictionary of mapped functions
        postprocess_template is a dictionary mapping a key to a function
        to run on the entry's field with the same key

        Arguments:
            entry: An entry extracted from template
            postprocess_template: a template of mapped functions
        """
        for key in postprocess_template.keys():
            value = entry[key]
            func = postprocess_template[key]
            entry[key] = func(value)
        return entry

    @staticmethod
    def restricted(entry, restrictions):
        """ Compare a flat dictionary(entry) to another(restrictions) or a list
        of restrictions.
        Return true if any of the entry's keys differ from it's counterpart in
        restriction
        """
        # TODO consider using regexp comparison, and or some function
        # No restrictions at all
        if not restrictions:
            return False
        if type(restrictions) == dict:
            restrictions = [restrictions]
        if type(restrictions) is not list:
            raise TypeError(
                "Restrictions must be a dictionary or a list of dictionaries"
            )
        # Iterate over all restrictions,
        # If any one restriction applied, return True
        for restriction in restrictions:
            # All keys match exactly
            for k in restriction.keys():
                if entry[k] != restriction[k]:
                    return True
        return False

    @staticmethod
    def extract(entry, template):
        """ Extract a single json entry to a templated dictionary

        Arguments:
            entry:  a single json item
            template: a jsonpath template of the format: 
            {'key1':'jsonpath_expr1', 'key2': 'jsonpath_expr2', ...}
        Returns:
            A populated template. if nested templates, only return the root
            matches
        """
        ret = {}
        for k in template.keys():
            jpath = template[k]
            jpath_obj = jsonpath_rw.parse(jpath)
            match = jpath_obj.find(entry)
            ret[k] = match[0].value
        return ret

    @staticmethod
    def dict_to_csv_entry(d, delim = ','):
        """ a flat dictionary to CSV entry """
        pass
        # keys = d.keys():


    @staticmethod
    def next_element(stream):
        pass


    @staticmethod
    def load_stream(
                stream,template,path='item',
                restrictions=None,
                output_file=None
                ):
        """ Load and preprocess a stream

        Arguments:
            stream: a stream (probably a file descriptior from open() )
            template: a dictionary of {key: jsonpath } 
                e.g. {'author':'$.user.name', 'text': '$.full_text',...}
            path: the jsonpath of the list containing these templates
                ('item' if stream is already this list )
            restrictions: reject if key differs
            output: a path to a json or a csv file to output to
                e.g. '/tmp/output.json' or '/tmp/output.csv'
        """
        ret = []
        entries = ijson.items(stream, path)
        for e in entries:
            entry = {}
            for k in template.keys():
                jpath = template[k]
                jpath_obj = jsonpath_rw.parse(jpath)
                match = jpath_obj.find(e)
                entry[k] = match[0].value

            if Parser.restricted(entry,restrictions):
                continue
            ret.append(entry)
        return ret


    @staticmethod
    def load_dataset(tweets_json,template, restrictions=None, deliminator = ", "):
        """ Open tweets json and parse into a CSV

        This is to open the whole file, non-stream-like

        Apply a template to extract jsonpath expressions to keys
        Only take first element of returned matched list.
        (It's all we need in this dataset's case)
        """
        ret = []
        with open(tweets_json,"r") as fp:
            tweets = json.load(fp)
        for t in tweets:
            entry = {}
            for key in template.keys():
                path_expr = parse(template[key])
                try:
                    # This returns a list of matches
                    match = path_expr.find(t)
                    # Take only first match!!!
                    entry[key] = match[0].value
                except TypeError as te:
                    logging.warning(te)
                except Exception as ex:
                    logging.error("Tweet: {}".format(t))
                    logging.error(ex)
            if not restricted(entry, restrictions):
                ret.append(entry)
        return ret
