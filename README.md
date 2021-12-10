#  CARP - CAR Pipeline
## A framework for building data pipelines.

These are utilities for web/datascraping from capture files.
This is for the first stage of a data pipeline.

These utilities provide methods for 
    - filtering out packets based on rules.
    - extracting relevant data objects, for example in embeded json, or in html

### HAR
Utils for parsing HAR files (HTTP Archive).

- Parser
- Restriction

### DOM
Utilities for parsing dom objects.

- Parser


### Text 
Utilities for parsing text objects


### JSON
Utilities for parsing JSON objects

### Examples

A HAR (HTTP Archive) file can be generated by firefox using the console.
<CTRL-Shift-e>
It stores request/response pairs of dictionaries captured by some browsing
session.

The *HAR parser* in Har/Parser.py is used to load the HAR capture file and apply
some rules  against those to filter out requests/responses

```python
har_parser = Har.Parser("/path/to/harfile.json")
```

OR 

```python
import json
with open("/path/to/harfile.json") as fp:
    jsn = json.load(fp)
    har_parser = Har.Parser(har_json = jsn)
```


A rule, defined Har/Restriction.py is a set of common selectors
```python
restriction = {
    'url_regexp': None,
    'mimetype_regex': None,
    'content_type': None,
    'content_regex': None,
}
```

url\_regexp defines some regular expression to match against the url.
**the other keys are not yet implemented. might not be useful.**


``` python
Restriction(restriction).match_entry(har_entry)
```
will return true if regexp match `har_entry['request']['url']`.

```python
# Find request/response entries where entry['request']['url'] match
# restriction['url_regexp']
entries = har_parser.find_entries(restriction)
```

You can also `filter_any(restrictions)` or `filter_out(restrictions)`,
where restrictions is a list of restrictions.

use these to select the requests which contain the data you wish to extract.
Once you isolated the interesting requests (probably using firefox's packet
inspector), filter the requests to the data source api endpoints.

Then use the **DOM Parser** to extract the relevant bits of information using
xpath expressions, templates and nested templates (usually forum comment
hierarchy).

To extract data from the Dom, we use xpath expressions, and dictionaries
mapping xpath expressions to keys.

```html
<div class="comment_container">
    <div class="author"> Boaty McBoatface </div>
    <div class="stats">
        <div class="score">5 points</div>
        <div class="time"> 5:50pm </div>
    </div>
    <div class="content">
        This is the comment
    </div>
</div>
```



```python
comment_container_xpath = "//div[contains(@class,'comment_container')]"
extract_template = {
    "author": "div[@class, 'author']//text()",
    "score": "div[@class='stats']/div[@class='score']//text()",
    "time": "div[@class='stats']/div[@class='time']//text()",
    "text": "div[contains(@class,'content')]//text()",
}
```

The Dom.Parser() class can be instantiated using an XML text, an lxml.etree
element, or a dictionary. a dictionary will be converted to xml internally.

```python
import json
import Dom
for entry in entries:
    url = entry['request']['url']
    txt = entry['response']['content']['text']

    # If txt is already a DOM text (an HTML probably)
    dom_parser = Dom.Parser(txt)

    # TODO fix this, you won't need to...
    # Or, if txt is of a JSON repsonse we load this to a dictionary first.
    # d = json.loads(txt)
    # dom_parser = Dom.Parser(d)
```


## Parsing JSON
_Stream parsing_: In order to parse large files, and potentially non-file data,
parsing is implemented as streams. 
Extracting mechanism is very similar to it's xpath counterpart (discussed
above), but implementinted using jsonpath syntax instead of xpath.

The Json.Parser instance contains two generators, one for the original json
_items_ and one for the extracted preprocessed _entries_.

**Example**
Given a json file in the form of a list of dictionaries, 
```json
[
    { 'id':1, 'name':'john', 'text':'Hello world'},
    { 'id':2, 'name':'john', 'text':'Goodbye world!'},
    // ...
]
```

We can iterate this by 

``` python
from car_scraper import Json

parser = Json.Parser('path/to/file.json')
with parser as p:
    for item in p.items:
        # Do something with entry
```

Note that usually, the data stream (the list) is in some nested node of the
dictionary.

``` json
{
    'company_name': 'Blahincorporate'
    'revenue': -5,
    employees:[
        { 'id':1, 'name':'john', 'text':'Hello world'},
        { 'id':2, 'name':'john', 'text':'Goodbye world!'},
    ]
}
```
In which case you could specify the root node as "employees", by passing the
prefix argument to Json.Parser using JSONPath syntax.


``` python
parser = Json.Parser('path/to/file.json','$.employees')
with parser as p:
    for item in p.items:
        # Do something with item
```

We can then extract the items to a dictionary by using a template
```python
template = {
	'id': '$.id',
	'text': '$.text',
	'lang': '$.lang',
}
with parser as p:
    for item in p.items:
        entry = p.extract(item, template)
```

We can also filter out entries by applying restrictions

```python
restriction = {
	'name': 'john'
}
with parser as p:
    for item in p.items:
        entry = p.extract(item, template)
		if p.restricted(entry):
			continue
```

As A shorthand for this we can instead pass the template and a list of
restrictions to the Json.Parser() constructor, then iterate over it's
instance's entries:



```python
template = {
	'id': '$.id',
	'text': '$.name',
	'lang': '$.text',
}
restriction = {
	'lang': 'en'
}
parser = Json.Parser(
    "path/to/file.json",
    prefix='item',
    template=template,
    restrictions = [restriction]
)

with parser as p:
    for entry in p.entries:
        # Do something with processed entry
```

Similarly, we can postprocess by mapping keys to some function

```python
def clean_text(text):
    return text.lower()


postprocess = {
    'text': clean_text
}

parser = Json.Parser(
    "path/to/file.json",
    template=template,
    postprocess_template= postprocess,
)

with parser as p:
    for entry in p.entries:
        # Do something with processed entry
```

We can use the allowed\_template to match the entry template against a
validation method function in the same way. The validation method must return a
True or False.


Suppose we have some *data.json* file
```json

    'people':[
        {'name': 'John', 'age':21},
        {'name': 'jim', 'age' :25},
        ...
    ]
```

We could stream this file, and match it's values against some True/False
function which we could iterate over using a generator pattern. 

e.g.

```python

def is_john(name):
    if 'john' in name.lower():
        return True
    return False

template = {
    'first_name':'$.name',
    'age':'$.age',
}

allowed = {
    'first_name':is_john
}
...
with open("data.json", "rb") as fp:
    res = Json.Parser.load_stream(
        fp,
        template,
        allowed_template = allowed,
        path='people.item',
        )
    for e in res:
        print e['first_name']

>>> John
```


TODO finish this... for now look at tests/integration/
