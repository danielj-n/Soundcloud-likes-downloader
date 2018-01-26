####TO FIX ENCODING: try just "ord"-ing every character and then figure out how many bytes that uses and then add them all up and make that less 255



#https://api-v2.soundcloud.com/users/40769393/likes?client_id=cnSYjxmeQCWsxjhf07BNwv5EUDe1jlNB&limit=100&offset=0&linked_partitioning=1&app_version=1512658529&app_locale=en
#at the end of the json you get a "next url" thing that gets you to the next URL
#the only thing you need to farm for the request is the client ID
#https://api.soundcloud.com/i1/tracks/359953751/streams?client_id=a3e059563d7fd3372b49b37f00a00bcf
#from here you get download links. Use the same client ID and the track num you get from above

import requests
import os.path


def get(sesh, url, params, headers, numOfAttempts) :
	returnData = None
	while (numOfAttempts) :
		try :
			returnData = sesh.get(url, params = params, headers = headers)
			break
		except :
			print "ya um fail"
			numOfAttemps -= 1
	return returnData

def parseLikesPage(rawData) :
	trackData = []
	for trackListing in rawData["collection"] :
		if "track" in trackListing :
			trackData.append({})
			track = trackListing["track"]
			trackData[-1]["trackID"] = track["id"]
			trackData[-1]["artist"] = track["user"]["username"] + " (" + track["user"]["permalink"] + ")"
			trackData[-1]["title"] = track["title"]
	return (trackData, rawData["next_href"])

def trueLength(string) :
	total = 0
	for char in string :
		if ord(char) > 256 :
			total += 4
		else :
			total += 1
	return total

def cutString(string, length) :
	cutString = ""
	total = 0
	for char in string :
		if ord(char) > 256 :
			total += 4
		else :
			total += 1
		if total > length :
			break
		cutString = cutString + char
	return cutString

userID = "40769393"
clientID = "cnSYjxmeQCWsxjhf07BNwv5EUDe1jlNB"
likesURL = "https://api-v2.soundcloud.com/users/" + userID + "/likes"
likesParams = {	"client_id": clientID,
		"limit": 100,
		"offset": 0,
		"linked_partitioning": 1,
		"app_version": 1512658529,
		"app_locale": "en"	}
sesh = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/60.0.3112.113 Chrome/60.0.3112.113 Safari/537.36"}
print "frick a noob"
data = get(sesh, likesURL, likesParams, headers, 5).json()

likesParams = {	"client_id": clientID,
		"linked_partitioning": 1,
		"app_version": 1512658529,
		"app_locale": "en"	}
while 1 :
	if data != None :
		trackData, nextHREF = parseLikesPage(data)
		for track in trackData :
			mp3Title = (track["artist"] + " -- " + track["title"] + ".mp3").replace("/", "\\\\")
			if trueLength(mp3Title) > 255 :
				mp3Title = cutString(mp3Title, 251) + ".mp3"
			if (not os.path.isfile(mp3Title)) :
				print mp3Title
				print trueLength(mp3Title)
				trackURL = "https://api.soundcloud.com/i1/tracks/" + str(track["trackID"]) + "/streams"
				trackParams = {"client_id": clientID}
				try :
					mp3URL = get(sesh, trackURL, trackParams, headers, 5).json()["http_mp3_128_url"]
					mp3 = get(sesh, mp3URL, {}, headers, 5).content
					f = open(mp3Title, "w+")
					f.write(mp3)
					f.close()
					print "dl complete"
				except :
					print "couldn't DL the track"
			else :
				print "dl skipped"
		print nextHREF
		data = get(sesh, nextHREF, likesParams, headers, 5).json()

