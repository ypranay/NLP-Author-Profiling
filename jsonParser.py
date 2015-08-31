import json
import re
nonspace = re.compile(r'\S')
def parseJSON(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = nonspace.search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded

blogdata = open('blogdata.json').read()
for entry in parseJSON(blogdata):
	print(entry["Sex"])