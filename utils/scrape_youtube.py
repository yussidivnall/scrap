import logging
import json
import argparse
from os import path
import jsonpath_rw_ext
from jsonpath_ng.ext import parser as json_parser
from car_scraper import Json
from car_scraper.Json.Helpers import del_path

def dump(entry):
    print(json.dumps(entry, indent=2))
    return entry

def build_comments(entry):
    comments = []
    found = json_parser.parse('$..commentRenderer').find(entry)
    for f in found:
        comment = {
            'author': f.value["authorText"]["simpleText"],
            'author_uri': f.value["authorEndpoint"]["browseEndpoint"]["canonicalBaseUrl"],
            'text': f.value["contentText"]["runs"][0]["text"],
            'published': f.value["publishedTimeText"]["runs"][0]["text"],
            'comment_id': f.value["commentId"],
            'likes': f.value["actionButtons"]["commentActionButtonsRenderer"]["likeButton"]["toggleButtonRenderer"]["accessibilityData"]["accessibilityData"]["label"],
            'video_id':f.value["publishedTimeText"]["runs"][0]["navigationEndpoint"]["watchEndpoint"]["videoId"],
        }
        comments.append(comment)
    return { 'comments': comments }
    # entry["comments"]=comments
    # return entry


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

def get_comments(har):
    template = {
        'comments':'$.comments',
        }
    har_entries_path= "log.entries.item"
    preprocess_list = [
        { 'func': reject_unrelated_entries },
        { 'func': unescape_content },
        { 'func': build_comments },
        # { 'func': dump },
    ]

    # postprocess_template = {
    #     'content': json.loads
    # }
    stream = Json.Parser.load_stream(
        har,
        template=template,
        path=har_entries_path,
        preprocess_list=preprocess_list,
    )
    return stream

def scrape(har_files):
    ret = []
    for har_file in har_files:
        with open(har_file, "rb") as fp:
            # for comments in scrape_comments(fp):
            for comments in get_comments(fp):
                ret.extend(comments["comments"])
    print(json.dumps(ret, indent=2))
    return ret

if __name__=='__main__':
    arg_parser = argparse.ArgumentParser(description="Parse a YouTube har capture")
    arg_parser.add_argument('har_files',nargs="+")
    args = arg_parser.parse_args()
    scrape(args.har_files)
