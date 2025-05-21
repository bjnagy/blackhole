import sys
from pathlib import Path
import re
from datetime import datetime
import json

import json

def main():
    # Main program logic goes here
    #print(f"Hello, {path}!")

    path = sys.argv[1]
    file = ""
    if len(sys.argv)>=3:
        file = sys.argv[2]

    path_universal = Path(path)
    #print("Your Python Path: ", path_universal)
    f = open(path_universal, encoding="utf8")
    #print(f.read())
    graph = json.load(f)
    blocks = graph["blocks"]
    output = []
    for block in blocks:
        if block["properties"] and "ls-type" in block["properties"] and block["properties"]["ls-type"] == "whiteboard-page":
            extract = None
        else:
            extract = flattenBlock(block)
        if extract:
            output = [*output, *extract]
    #unit tests:
    #print(blocks[0])
    # extract = flattenBlock(blocks[0])
    # print(extract)
    f.close()
    if file:
        with open(file, 'w') as f:
           print(json.dumps(output), file=f)
    else:
        print(json.dumps(output))

def flattenBlock(block):
    extract = []
    newChildren = []
    if block["children"]:
        for child in block["children"]:
            newChildren.append(child["id"])
            extract = [*extract, *flattenBlock(child)]
        block["children"] = newChildren
    extract.append(block)
    return extract


if __name__ == "__main__":
    main()