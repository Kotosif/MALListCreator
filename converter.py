# pylint: disable=W0632 
from lxml import etree as ET
from sys import argv
import requests
from requests.auth import HTTPBasicAuth
from gsearch import GoogleAPI

# Constants
MALAPIURL = "https://myanimelist.net/api/anime/search.xml?q="
conf = "login.txt"

#Global variables
username = ""
password = ""

def setUserCredentials(conf):
    # conf - string filename
    global username, password
    text = open(conf, 'r')
    credentials = text.readline().split(":")
    username, password = credentials[0], credentials[1]
    text.close()

def buildAnimeElement(id, name):
    # id - string id of anime
    # name - name of anime
    anime = ET.Element("anime")
    series_anime_id = ET.SubElement(anime, "series_animedb_id")
    series_anime_id.text = id
    series_title = ET.SubElement(anime, "series_title")
    series_title.text = ET.CDATA(name)
    my_status = ET.SubElement(anime, "my_status")
    my_status.text = "Completed"
    update_on_import = ET.SubElement(anime, "update_on_import")
    update_on_import.text = "1"
    return anime

def addAnime(treeNode, name):
    # treeNode - XML node
    # name - string argument

    # Preprocess the query to remove extra nonsense
    query = name.strip().lower()
    if (query.endswith("s2")):
        query = query[:-2] + "2"
    elif (query.endswith("s1")):
        query = query[:-2].strip()
    url = MALAPIURL + "+".join(query.split())
    response = requests.get(url,
                            auth=HTTPBasicAuth(username, password))
    text = response.text

    # If rate limit reach keep trying
    while (text.strip() == "Too Many Requests"):
        response = requests.get(url,
                        auth=HTTPBasicAuth(username, password))
        text = response.text
    
    if (response.status_code == 204):
        print("Unable to find metadata for title: %s url: %s" % (name, url))
        return False

    # Parse the XML response
    parser = ET.XMLParser(encoding="utf-8")
    try:
        treeRoot = ET.XML(text.encode("utf-8"), parser)
        id = treeRoot[0][0].text
        title = treeRoot[0][1].text
        name = title
        treeNode.append(buildAnimeElement(id, name))
        return True
    except ET.XMLSyntaxError:
        print("Parse error: text = %s" % text.strip())
        print("Title: %s" % name)
    return False

def processGoogleSearchResult(results):
    # result - string Google search result
    splitters = ['(', '-'] # in order of precedence
    processedResults = []
    for result in results:
        for splitter in splitters:
            if splitter in result:
                processedResult = result.split(splitter)
                processedResults.append(processedResult[0].strip())
    return processedResults


def writeFailuresToFile(failures):
    failLog = open("failed.txt", "w")
    for failure in failures:
        failLog.write(failure)
    print("There were some titles that failed to be added. These have been printed to the file failed.txt")

if __name__ == "__main__":
    script, xmlfile, txtfile = argv
    parser = ET.XMLParser(strip_cdata=False, encoding="utf-8", remove_blank_text=True)
    xml = open(xmlfile, 'r')
    # re-encode the file as lxml doesn't like encoding definitions
    # parser must have matching encoding
    root = ET.XML(xml.read().encode('utf-8'), parser)
    animelist = open(txtfile, 'r')
    setUserCredentials(conf)
    count = 0
    failures = []
    titles = []
    for line in animelist:
        segments = line.split('.')
        if (len(segments) < 2):
            print("Badly formatted line: %s" % line)
            continue
        success = addAnime(root, segments[1].strip())
        if (success):
            count += 1
            print("Added %d" % count)
        else:
            failures.append(line)
            titles.append(segments[1].strip())
    f = open("out.xml", 'wb') #opens file in bytes mode
    f.write(ET.tostring(root, pretty_print=True))
    if (len(failures) > 0):
        carryOn = input("Some titles failed. You probably spelled their titles wrong. Try using Google Search to find their names? [y/n]\n")
        if (carryOn == 'y'):
            finalFailures = []
            for title in titles:
                api = GoogleAPI()
                # The first result will be enough
                results = api.search(title, site = 'myanimelist.net')
                if len(results) == 0:
                    print("No results found on Google.")
                else:
                    # Checking from the first 3 results will be enough
                    results = processGoogleSearchResult(results[0:4])
                    success = False
                    for i in range(0, 3):
                        success = addAnime(root, results[i])
                        if success:
                            break
                    if (success):
                        count += 1
                        print("Added %d" % count)
                    else:
                        finalFailures.append(title)
            f = open("out.xml", 'wb')
            f.write(ET.tostring(root, pretty_print=True))
            if len(finalFailures) > 0:
                writeFailuresToFile(finalFailures)
                exit()
        elif (carryOn != 'y' and carryOn != 'n'):
            print("Didn't understand the input.")
        writeFailuresToFile(failures)
        



