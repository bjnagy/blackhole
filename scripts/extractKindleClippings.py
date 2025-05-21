import sys
from pathlib import Path
import re
from datetime import datetime

def main(path):
    # Main program logic goes here
    #print(f"Hello, {path}!")

    path_universal = Path(path)
    #print("Your Python Path: ", path_universal)
    f = open(path_universal, encoding="utf8")
    #print(f.read())
    clippings = f.read()
    output = []
    for x in clippings.split("==========\n"):
        extract = extractClipping(x)
        if extract:
            output.append(extract)
    #unit tests:
    #extractClipping(clippings.split("==========\n")[0])
    #extractClipping(clippings.split("==========\n")[-2])
    f.close()
    print(output, file=sys.stdout)

def extractClipping(block):
    extract = {}
    locDetails = {}
    try:
        extract["author"] = re.search(r"[^.]*\((.*?)\)$", block.splitlines()[0]).group(1).strip()
        extract["title"] = re.sub(r"\(" + re.escape(extract["author"]) + r"\)$", "", block.splitlines()[0]).strip().lstrip('\ufeff')
        details = block.splitlines()[1].split(" | ")
        extract["type"] = re.search("- Your (.*) on", details[0]).group(1).strip()
        details[0] = re.sub(r"- Your (.*) on", "", details[0])
        extractPageLoc(details[0], locDetails)
        if details[1].__contains__("Location"):
            extractPageLoc(details[1], locDetails)
        extract["date"] = datetime.strptime(details[-1], "Added on %A, %B %d, %Y %I:%M:%S %p").isoformat()
        extract["content"] = block.splitlines()[-1]
        extract = {**extract, **locDetails}
        #print(extract)
    except:
        title = ""
    if extract:
        return extract

def extractPageLoc(loc, locDetails):
    pageStart = None
    pageEnd = None
    locationStart = None
    locationEnd = None
    if loc.__contains__("page"):
        if loc.__contains__("-"):
            pageStart = loc.replace("page ","").split("-")[0].strip()
            pageEnd = loc.replace("page ","").split("-")[1].strip()
        else:
            pageStart = loc.replace("page ","").strip()
            pageEnd = loc.replace("page ","").strip()
    else:
        if loc.__contains__("-"):
            locationStart = loc.replace("Location ","").split("-")[0].strip()
            locationEnd = loc.replace("Location ","").split("-")[1].strip()
        else:
            locationStart = loc.replace("Location ","").strip()
            locationEnd = loc.replace("Location ","").strip()
    replaceNullDictValue(locDetails,"pageStart", pageStart)
    replaceNullDictValue(locDetails,"pageEnd", pageEnd)
    replaceNullDictValue(locDetails,"locationStart", locationStart)
    replaceNullDictValue(locDetails,"locationEnd", locationEnd)

def replaceNullDictValue(dict, key, newValue):
    if key in dict:
        if newValue:
            dict[key] = newValue
    else:
        dict[key] = newValue

if __name__ == "__main__":
    main(sys.argv[1])