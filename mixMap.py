import tkinter
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json

# Place your Google API key inside the quotes
GOOGLEAPIKEY = ""


class Globals:

    rootWindow = None
    mapLabel = None
    defaultLocation = "London"
    mapLocation = defaultLocation
    mapFileName = 'googlemap.gif'
    mapSize = 400
    zoomLevel = 9
    mapType = 'roadmap'
    index = 0


def readGeoDict():
    global geoDict
    try:
        dictInFile = open('geodict.json')
    except:
        geoDict = {}
    else:
        jsonString = dictInFile.read()
        geoDict = json.loads(jsonString)
        dictInFile.close()


def saveGeoDict():
    global jsonString
    print('saving geodict.json')
    dictOutFile = open('geodict.json', 'w')
    jsonString = json.dumps(geoDict)
    dictOutFile.write(jsonString)
    dictOutFile.close()


def geocodeAddress(addressString):
    urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
    geoURL = urlbase + quote_plus(addressString)
    geoURL = geoURL + "&key=" + GOOGLEAPIKEY

    # required (non-secure) security stuff for use of urlopen
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
    jsonResult = json.loads(stringResultFromGoogle)
    if (jsonResult['status'] != "OK"):
        print(
            "Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
        # this prevents crash in retrieveMapFromGoogle -
        # yields maps with lat/lon center at 0.0, 0.0
        result = (0.0, 0.0)
    else:
        loc = jsonResult['results'][0]['geometry']['location']
        result = (float(loc['lat']), float(loc['lng']))
    return result


# MODIFY THIS
def getMapUrl():
    lat, lng = geocodeAddress(Globals.mapLocation)
    urlbase = "http://maps.google.com/maps/api/staticmap?"
    args = "center={},{}&zoom={}&size={}x{}&maptype={}&format=gif{}".format(
        lat, lng, Globals.zoomLevel, Globals.mapSize, Globals.mapSize, Globals.mapType, finalString)
    args = args + "&key=" + GOOGLEAPIKEY
    mapURL = urlbase + args
    return mapURL


def retrieveMapFromGoogle():
    url = getMapUrl()
    urlretrieve(url, Globals.mapFileName)


def displayMap():
    retrieveMapFromGoogle()
    mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
    Globals.mapLabel.configure(image=mapImage)
    # next line necessary to "prevent (image) from being garbage collected"
    # http://effbot.org/tkinterbook/label.htm
    Globals.mapLabel.mapImage = mapImage


def readEntryAndDisplayMap():

    Globals.mapLocation = cityEntry.get()
    displayMap()
    cityEntry.delete(0, tkinter.END)


def zoomIn():
    Globals.zoomLevel = Globals.zoomLevel + 1
    displayMap()


def zoomOut():
    Globals.zoomLevel = Globals.zoomLevel - 1
    displayMap()


def satelliteMaptype():
    Globals.mapType = 'satellite'
    displayMap()


def roadmapMaptype():
    Globals.mapType = 'roadmap'
    displayMap()


def terrainMaptype():
    Globals.mapType = 'terrain'
    displayMap()


def hybridMaptype():
    Globals.mapType = 'hybrid'
    displayMap()


def generateMarkerString(currentTweetIndex, tweetLatLonList, mapCenterLatLon):
    finalString = ''
    localIndex = 0
    for item in tweetLatLonList:
        color = None
        size = None
        if localIndex != currentTweetIndex:
            color = 'green'
            size = 'small'
        else:
            color = 'red'
            size = 'medium'
        if (item != None and item != 'None'):
            latitude = item[0]
            longitude = item[1]
            markersString = "&markers=color:{}|size:{}|{},{}".format(
                color, size, latitude, longitude)
            finalString = finalString + markersString
        localIndex += 1
    return finalString


def initializeGUIetc():
    global cityEntry
    global choiceVar  # It wouldn't work without this. Not sure why.
    Globals.rootWindow = tkinter.Tk()
    Globals.rootWindow.title("HW10")
    choiceVar = tkinter. StringVar()
    # ---------------- Frames  ------------------------------
    # Use multiple frames for better presentation
    mainFrame = tkinter.Frame(Globals.rootWindow)
    radioFrame = tkinter.Frame()
    mapFrame = tkinter.Frame()
    zoomFrame = tkinter.Frame()

    # ------------------ Entry & Labels ------------------------------
    cityEntry = tkinter.Entry(mainFrame, width=20, font=('Calibri 12'))
    cityEntryLabel = tkinter.Label(mainFrame, text='Please enter a location:')
    zoomLabel = tkinter.Label(zoomFrame, text='Zoom In/Out')

    # ----------------   Buttons -------------------------------------
    readEntryAndDisplayMapButton = tkinter.Button(
        mainFrame, text="Show me the map!", command=readEntryAndDisplayMap)
    roadmapChoice = tkinter.Radiobutton(
        radioFrame, text="roadmap", variable=choiceVar, value='1', command=roadmapMaptype)
    satelliteChoice = tkinter.Radiobutton(
        radioFrame, text="satellite", variable=choiceVar, value='2', command=satelliteMaptype)
    hybridChoice = tkinter.Radiobutton(
        radioFrame, text="hybrid", variable=choiceVar, value='3', command=hybridMaptype)
    terrainChoice = tkinter.Radiobutton(
        radioFrame, text="terrain", variable=choiceVar, value='4', command=terrainMaptype)
    plusButton = tkinter.Button(zoomFrame, text='+', command=zoomIn)
    minusButton = tkinter.Button(zoomFrame, text='-', command=zoomOut)
    # ----------------------------- Pack ---------------------------------
    mainFrame.pack(fill=tkinter.BOTH)
    radioFrame.pack()
    mapFrame.pack(fill=tkinter.X)
    zoomFrame.pack()

    cityEntryLabel.pack(fill=tkinter.X)
    cityEntry.pack()
    readEntryAndDisplayMapButton.pack()

    roadmapChoice.pack(side=tkinter.LEFT, padx=5)
    satelliteChoice.pack(side=tkinter.LEFT, padx=5)
    hybridChoice.pack(side=tkinter.LEFT, padx=5)
    terrainChoice.pack(side=tkinter.LEFT, padx=5)

    zoomLabel.pack(side=tkinter.BOTTOM)
    plusButton.pack(ipadx=20, side=tkinter.LEFT)
    minusButton.pack(ipadx=20, pady=5, side=tkinter.LEFT)

    # we use a tkinter Label to display the map image
    Globals.mapLabel = tkinter.Label(
        mapFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
    Globals.mapLabel.pack(padx=30, pady=30, side=tkinter.BOTTOM)

    choiceVar.set('1')


def startMap():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()


# Testing
print(generateMarkerString(1, [[40.7452888, -73.9864273],
                               None, [40.76056, -73.9659]], [40.758895, -73.985131]))
# startMap()
