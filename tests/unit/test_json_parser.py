import pytest
import re
from car_scraper import Json

# @pytest.mark.skip(reason="Takes too long in dev")
def test_stream():
    test_data = "./tests/test_data/nazi_tweets_sample.json"
    entries_template = {
        'id': '$.id',
        'text': '$.full_text',
        'lang': '$.lang',
    }
    restrictions = {
        'lang':'en'
    }

    with open(test_data, "rb") as fp:
        res = Json.Parser.load_stream(
            fp,
            template = entries_template,
            path='item',
            restrictions = restrictions
            )
        for e in res:
            print(e)
        # print(res)
    #     print(fp)
    #     pass
    # assert False

# @pytest.mark.skip(reason="Takes too long in dev")
def test_class_streaming():
    test_data = "./tests/test_data/nazi_tweets_sample.json"

    entries_template = {
        'id': '$.id',
        'text': '$.full_text',
        'lang': '$.lang',
    }

    restrictions = {
        'lang':'en'
    }
    # parser = Json.Parser(test_data,'item')
    parser = Json.Parser(test_data)
    with parser as p:
        for item in p.items:
            print("-----------")
            entry = p.extract(item,entries_template)
            assert 'id' in entry
            assert 'text' in entry
            assert 'lang' in entry
            if p.restricted(entry, restrictions):
                assert entry['lang'] != 'en'
                print(entry)
            else:
                assert entry['lang'] == 'en'
                print(entry)

# @pytest.mark.skip(reason="Takes too long in dev")
def test_iterating():
    test_data = "./tests/test_data/nazi_tweets_sample.json"

    jpath_template = {
        'id': '$.id',
        'text': '$.full_text',
        'lang': '$.lang',
    }

    restriction = {
        'lang':'en'
    }
    parser = Json.Parser(
        test_data,
        prefix='item',
        template=jpath_template,
        restrictions = [restriction]
    )
    with parser as p:
        # for item in p.items:
        for entry in p.entries:
            print(entry)
            assert entry['lang'] == 'en'
    # assert False

import re

def fix_text(txt):
    """ Some postprocessing function """
    txt = txt.lower()
    # Remove all @mentions at start of tweets 
    txt = re.sub(r"^(@\w+\s+)+", "", txt)
    # Remove all numbers
    txt = re.sub(r"[0-9]*", "", txt)
    txt = re.sub(r"\s+"," ", txt)
    return txt

# @pytest.mark.skip(reason="Takes too long in dev")
def test_preprocess_function():
    test_data = "./tests/test_data/nazi_tweets_sample.json"

    jpath_template = {
        'id': '$.id',
        'text': '$.full_text',
        'lang': '$.lang',
    }
    restriction = {
        'lang':'en'
    }
    postprocess = {
        'text': fix_text
    }
    parser = Json.Parser(
        test_data,
        prefix='item',
        template=jpath_template,
        restrictions = [restriction],
        postprocess_template = postprocess,
    )
    with parser as p:
        # for item in p.items:
        for entry in p.entries:
            # print(entry)
            txt = entry['text']
            # txt = fix_text(txt)
            print(txt)
            assert not txt.startswith("@")
            assert txt == txt.lower()
        # assert False

# @pytest.mark.skip(reason="Takes too long in dev")
def test_extract_returns_multiple_items():
    data = {
        'l':[
            {'entry':{'id':1}},
            {'entry':{'id':2}},
            {'entry':{'id':3}},
        ]
    }
    template = {
        'm': '$.l[*]',
    }
    extracted = Json.Parser.extract(data, template)
    print(extracted['m'])
    print(len(extracted['m']))
    assert len(extracted['m']) == 3

import jsonpath_rw_ext as jp
def test_jsonpath_rw_ext():
    data = {
        'l':[
            {'entry':{'id':1}},
            {'entry':{'id':2}},
            {'entry':{'id':3}},
        ]
    }
    jpath = "$..entry[*]"
    m = jp.match(jpath, data)
    for e in m:
        print(e)
        assert 'id' in e.keys()
        assert e['id'] in [1,2,3]
    # p = jp.parser.ExtentedJsonPathParser().parse(jpath).find(data)
    # print(m)
    # assert False


def test_extract_jpath():
    data = {
        'l':[
            {'entry':{'id':1}},
            {'entry':{'id':2}},
            {'entry':{'id':3}},
        ]
    }
    jpath = "$..entry[*]"
    extracted = Json.Parser.jsonpath_find(jpath, data)
    print("Extracted:{}".format(extracted))
    for e in extracted:
        print("entry:{}".format(e))
        print(type(e))
    assert len(extracted) == 3

    jpath = "$.l[2]"
    extracted = Json.Parser.jsonpath_find(jpath, data)
    print("Extracted:{}".format(extracted))
    assert len(extracted) == 1


def test_allowed():

    def is_old(age):
        if age > 49:
            return True
        return False

    def is_mouthy(txt):
        if 'Fucking' in txt:
            return True
        return False

    entry = {
        'name': 'John',
        'text': 'Fucking hell this is terrible',
        'age': 50,
    }

    allowed_template = {
        'age': is_old,
        'text': is_mouthy
    }
    assert Json.Parser.allowed(entry, allowed_template)

    entry = {
        'name': 'John',
        'text': 'Bloody hell this is terrible',
        'age': 49,
    }
    assert not Json.Parser.allowed(entry, allowed_template)
    with pytest.raises(ValueError) as verr:
        allowed_template = {
            'agei': is_old,
            'text': is_mouthy
        }
        Json.Parser.allowed(entry, allowed_template)


def test_stream_allowed():
    import re
    har_file = "tests/test_data/forum.red.1.har"


    def selected_endpoints(url):
        url_regexps = [
            '^.*.forums\.red\/i\/.*'
        ]
        for reg in url_regexps:
            if re.match(reg, url):
                return True
        return False


    entries_template={
        'url': '$.request.url',
        'text': '$.response.content.text',
    }
    allowed = {
        'url': selected_endpoints,
    }


    with open(har_file, "rb") as fp:
        res = Json.Parser.load_stream(
            fp,
            entries_template,
            allowed_template = allowed,
            path='log.entries.item',
            # restrictions = restrictions
            )
        print(res)
        for e in res:
            assert 'https://www.forums.red/i' in e['url']
            print(e['url'])
