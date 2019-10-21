from car_scraper import Json

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

