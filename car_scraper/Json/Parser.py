
import logging
import csv
import json
import ijson
import jsonpath_rw
# from jsonpath_rw import jsonpath, parse

class Parser():

    def __init__(self, json_file, prefix='item'):
        self.input_file = open(json_file, 'rb')
        self.prefix = prefix
        self.items = None

    def __iter__(self):
        return self

    def __enter__(self):
        self.items = ijson.items(self.input_file, self.prefix)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.input_file.close()


    @staticmethod
    def restricted(entry, restriction):
        # No restrictions at all
        if not restriction:
            return False
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
        """ Open the nazi tweets json and parse into a CSV

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
                print("------------------------------")
                print("Getting {}".format(entry))
                ret.append(entry)
        return ret
            # pass
            # tweet_id = str(e['id'])
            # created = e['created_at']
            # text = e['full_text']
            # lang = e['lang']
            # in_reply_to_status = str(e['in_reply_to_status_id'])
            # user_id = str(e['user']['id'])
            # screen_name = str(e['user']['screen_name'])
            # timezone = e['user']['time_zone']
            # location = e['user']['location']
            # if not restrictions:
            #     r = deliminator.join(
            #         [tweet_id, created, text, lang,
            #          in_reply_to_status, user_id,
            #          screen_name,timezone,location])
            #     print(r)
        pass
