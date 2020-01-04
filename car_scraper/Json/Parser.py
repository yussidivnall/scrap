import logging
import csv
import json
import ijson
import jsonpath_rw_ext
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
            yield entry

    @staticmethod
    def jsonpath_find(jpath, data):
        """ A helper function to match a json_path against dictionary data
        Returns the matched value if a single entry, or a list of matched
        values if more then one

        Arguments:
            jpath: A string with a jsonpath expression conforming to
                   jsonpath_rw_ext sytax)
            data: The dictionary to search

        Returns:
            The matched value or a list of values
        """
        jpath_obj = jsonpath_rw_ext.parse(jpath)
        match = jpath_obj.find(data)

        # Only one matched, return value
        if len(match) == 1:
            return match[0].value
        # Multiple matched, add value to list
        elif len(match) > 1:
            ret = []
            for m in match:
                ret.append(m.value)
            return ret
        else:
            raise ValueError(
                "JSON_Path expression {} not matched".format(jpath)
                )

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

        Arguments:
            entry:
            restrictions:
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
    def allowed(entry, allowed_template):
        """ Returns True if all keys in allowed_template match to their
        counterpart in entry.

        Arguments:
            entry: a dictionary mapping some keys to some to some values.
               e.g entry = { 'name': 'John', 'age': 30 }
            restriction: a dictionary mapping a subset of entry's keys to a
            functions which return True or False
                e.g. 
                ```
                def can_drink(age)
                    if age > 18:
                        return True
                    else return false

                allowed_template = {
                    'age': can_drink
                }
                ```
            returns:
                True if all restrictions defined in allowed_template
                valuate to True, False otherwise
        """
        allowed_keys = list(allowed_template.keys())
        entry_keys = list(entry.keys())
        # Ensures all keys are present in entry
        if not set(allowed_keys) <= set(entry_keys):
            raise ValueError(
                "some keys in {} are missing from {}".format(
                    allowed_keys,
                    entry_keys
                )
            )
        for k in allowed_keys:
            func = allowed_template[k]
            value = entry[k]
            if not func(value):
                return False
        return True

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
            ret[k] = Parser.jsonpath_find(jpath, entry)
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
                stream,
                template,
                path='item',
                allowed_template=None,
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
                try:
                    entry[k] = Parser.jsonpath_find(jpath, e)
                except ValueError as verr:
                    logging.warning("No value given for {}, setting to None".format(k))
                    entry[k]=None
            if allowed_template and not Parser.allowed(entry, allowed_template):
                # allowed_template is defined but at least one value in entry is not allowed()
                continue
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
                    print(len(match))
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
