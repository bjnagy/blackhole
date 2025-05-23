import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from collections import OrderedDict

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}


def getEventDetails(eventId):
    # print("eventId: ", eventId)
    details = {'eventId': eventId}
    event = requests.get(f'https://www.cervistech.com/acts/webreg/eventdetail.php?event_id={eventId}&org_id=0254&hide_buttons=yes&back=min',headers=headers)
    soup = BeautifulSoup(event.content, "html.parser")
    slots = []

    try:
        text = "Opportunity Name:"
        element = soup.find(lambda tag: tag.name == "td" and text in tag.text)
        details['opportunityName'] = element.get_text().replace(text,"").strip()
    except:
        element

    try:
        text = "Description:"
        element = soup.find(lambda tag: tag.name == "td" and text in tag.text)
        details['description'] = element.get_text().replace(text,"").strip()
    except:
        element

    try:
        text = "Date/Time:"
        element = soup.find(lambda tag: tag.name == "tr" and text in tag.text)
        tempVal = element.get_text().replace(text,"").strip()         #	Tue, May 20, 2025 - 7:30 PM to 8:30 PM
        slot = parseEventTime(tempVal)

        text = "Spots Available:"
        element = soup.find(lambda tag: tag.name == "tr" and text in tag.text)
        tempVal = element.get_text().replace(text,"").strip()
        slot['SpotsAvailable'] = parseSlotsAvailable(tempVal)

        slots.append(slot)
    except:
        element

    try:
        text = "Meeting Location:"
        element = soup.find(lambda tag: tag.name == "tr" and text in tag.text)
        details['meetingLocationDesc'] = element.get_text().replace(text,"").replace("View Map / Get Directions","").strip()
        details['meetingLocation'] = element.find("a")["href"]
    except:
        element

    try:
        text = "Organizer:"
        element = soup.find(lambda tag: tag.name == "tr" and text in tag.text)
        details['organizer'] = parseOrganizer(element) # element.get_text().replace(text,"") #.strip()
    except:
        element

    try:
        text = "Category:"
        element = soup.find(lambda tag: tag.name == "tr" and text in tag.text)
        #print(element.get_text())
        details['category'] = element.get_text().replace(text,"").strip()
    except:
        element

    #timeslots (doesn't always exist) 2596, 2591, 2503 

    slots = [*slots, *extractSlotsTable(soup.find('table', id='result_list'))]
    details['slots'] = slots

    return details

def parseEventTime(text):
    retDict = {}
    text = text.replace("\xa0"," ").strip()
    eventDate = text.split(" - ")[0]
    startTime = text.split(" - ")[1].split(" to ")[0]
    endTime = text.split(" - ")[1].split(" to ")[1]
    retDict['startTime'] = datetime.strptime(eventDate + " " + startTime, "%a, %b %d, %Y %I:%M %p").isoformat()
    retDict['EndTime'] = datetime.strptime(eventDate + " " +  endTime, "%a, %b %d, %Y %I:%M %p").isoformat()
    return retDict

def parseSlotsAvailable(text):
    retval = ''
    parse = BeautifulSoup(text,"html.parser").get_text()
    if parse == 'Unlimited':
        retval = 99
    elif parse == 'Waitlist':
        retval = -1
    elif parse == 'Event Full':
        retval = 0
    else:
        retval = parse
    return retval

def parseOrganizer(element):
    child = element.find_all("td")[1]
    retDict = {}
    retDict["organizerName"] = child.contents[0]
    retDict["organizerEmail"] = child.contents[2]
    try:
        retDict["organizerPhone"] = child.contents[4]
    except:
        retDict["organizerPhone"] = ""
    return retDict

def extractSlotsTable(table):
    # alternative method: https://stackoverflow.com/a/51657193
    slots = []
    if table:
        rows = table.find_all("tr", class_="over")
        for row in rows:
            children = row.find_all("td")
            #first td has startTime, endTime, and activityName separated from the first two by a <br>
            slot = {}
            slot = parseEventTime(children[0].contents[0])
            #slot["dateTime"] = parseEventTime(children[0].contents[0])
            try:
                slot["activity"] = children[0].contents[2] #not always an activity present
            except:
                slot["activity"] = ""
            slotInfo = row['title'].replace("header=[Slot Information] body=","").replace("[","").replace("]","")
            slotInfos = string_to_dict(slotInfo, "<br />", ":")
            slotInfos = {key.replace(" ",""): value for key, value in slotInfos.items()}
            slotInfos["SpotsAvailable"] = parseSlotsAvailable(slotInfos["SpotsAvailable"])
            slot = {**slot, **slotInfos}
            slots.append(slot)
    #print(slots)
    return slots

def string_to_dict(data, row_sep='\n', col_sep='=', key_type=str, value_type=str):
    return {
        key_type(pair.split(col_sep)[0].strip()): value_type(pair.split(col_sep)[1].strip())
        for pair in data.split(row_sep) if col_sep in pair
    }


url = 'https://www.cervistech.com/acts/webreg/eventwebreglist.php?org_id=0254'
response = requests.get(url,headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Check the status code
print(f"Status Code: {response.status_code}")

links = soup.find_all('a')
events = []

#unit tests
# events.append(getEventDetails(3))
# events.append(getEventDetails(2507))
# events.append(getEventDetails(2543))
# events.append(getEventDetails(2523))
# events.append(getEventDetails(2503))
# events.append(getEventDetails(2370))

for link in links:
    if 'event_id' in link['href']:
        parsed = urlparse(link['href'])
        id = parse_qs(parsed.query)['event_id'][0]
        events.append(getEventDetails(id))

print(events)

# Print the response content
#print(f"Content: {response.text}")
