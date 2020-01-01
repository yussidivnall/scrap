import pytest
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
        print(res)
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
