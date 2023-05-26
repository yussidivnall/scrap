import logging
import json
import argparse
from os import path
import jsonpath_rw_ext
from jsonpath_ng.ext import parser as json_parser
from car_scraper import Json
from car_scraper.Json.Helpers import del_path




def find_path(entry, key, expression):

    found = json_parser.parse(expression).find(entry)
    # found = jsonpath_rw_ext.parse(expression).find(entry)
    for f in found:
        print(f.full_path)
        print(json.dumps(f.value, indent=2))
    return entry

def build_comments(entry):
    found = json_parser.parse('$..commentThreadRenderer.comment.commentRenderer').find(entry)
    entry["comments"]=[]
    for f in found:
        comment = {
            'author': f.value["authorText"]["simpleText"],
            'author_uri': f.value["authorEndpoint"]["browseEndpoint"]["canonicalBaseUrl"],
            'text': f.value["contentText"]["runs"][0]["text"],
            'published': f.value["publishedTimeText"]["runs"][0]["text"],
            'comment_id': f.value["commentId"],
            'likes': f.value["actionButtons"]["commentActionButtonsRenderer"]["likeButton"]["toggleButtonRenderer"]["accessibilityData"]["accessibilityData"]["label"],
            'video_id':f.value["publishedTimeText"]["runs"][0]["navigationEndpoint"]["watchEndpoint"]["videoId"],
            # 'full_entry': f.value
        }
        # print(json.dumps(comment, indent=2))
        entry["comments"].append(comment)
    return entry


def reject_unrelated_entries(entry):
    url = entry['request']['url']
    if "youtube.com/youtubei/v1/next?key=" in url:
        return entry
    return None

def unescape_content(entry):
    escaped_content = entry['response']['content']['text']
    entry['response']['content']['text'] = json.loads(escaped_content)
    return entry

def remove_unused_keys(entry, unused_keys):
    for jp in unused_keys:
        query = jsonpath_rw_ext.parse(jp)
        found = query.find(entry)
        for f in found:
            try:
                del_path(entry, str(f.full_path))
            except KeyError as kerr:
                logging.debug(r"delete key error for {f.full_path}")
                logging.error(kerr)
    # print(json.dumps(entry,indent=2))
    return entry

def get_comment_har_entries(har):
    template = {
        'url': '$.request.url',
        'content':'$.response.content.text'
        }
    har_entries_path= "log.entries.item"
    preprocess_list = [
        { 'func': reject_unrelated_entries },
        { 'func': unescape_content },
        # { 'func': find_path,
        #   'args': {
        #       'key': 'text',
        #       # 'expression': '$.response.content.text.onResponseReceivedEndpoints.*.text[?(@.text =~ ".*Report.*")]'
        #       'expression': '$..commentThreadRenderer.comment.commentRenderer'
        #       # 'expression': '$.response.content.text.onResponseReceivedEndpoints..commentThreadRenderer.comment.commentRenderer'
        #       # 'expression': '$.response.content.text.onResponseReceivedEndpoints..commentThreadRenderer.comment.commentRenderer..contentText..text'
        #       # 'expression': '$.response.content.text.onResponseReceivedEndpoints..contentText..text'
        #       # 'expression': '$..text'
        #   }
        # },
        # {
        #     'func': remove_unused_keys,
        #     'args': {
        #         'unused_keys': [
        #             '$.request',
        #             '$.pageref',
        #             '$.startDateTime',
        #             '$.response.headers',
        #             '$.response.cookies',
        #             '$..emojiIds',
        #         ]
        #     }
        # },
        { 'func': build_comments },
    ]

    # postprocess_template = {
    #     'content': json.loads
    # }
    stream = Json.Parser.load_stream(
        har,
        template=template,
        path=har_entries_path,
        preprocess_list=preprocess_list,
        # postprocess_template=postprocess_template,
    )
    return stream
    #for entry in stream:
    #    yield entry
    #    #print(entry)

def get_comments(content):
    template = {
        'text': '$.*.contentText.runs'
    }

    stream = Json.Parser.load_stream(
        content,
        template=template
    )
    # for e in stream:
    #     print(e['text'])


def scrape_comments(har):
    stream = get_comment_har_entries(har)
    for entry in stream:
        # print(entry['url'])
        # print(json.dumps(entry['content'], indent=2))
        pass

def scrape_comment_replies(har):
    pass


def scrape(har_files):
    for har_file in har_files:
        with open(har_file, "rb") as fp:
            scrape_comments(fp)

if __name__=='__main__':
    arg_parser = argparse.ArgumentParser(description="Parse a YouTube har capture")
    arg_parser.add_argument('har_files',nargs="+")
    args = arg_parser.parse_args()
    scrape(args.har_files)
