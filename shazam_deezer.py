import json
import requests
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Paste "codever" value after equal sign below in between "":
codever = ""

# Paste "inid" value after equal sign below in between "":
inid = ""

# Recreate the Cookie and create the headers for the requests
cookie = 'geoip_country=FR; geoip_lat=46.196; geoip_long=6.240; codever=' + codever
headers = {
	'authority': 'www.shazam.com',
	'dnt': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
	'content-type': 'application/json',
	'accept': '*/*',
	'sec-fetch-site': 'same-origin',
	'sec-fetch-mode': 'cors',
	'referer': 'https://www.shazam.com/myshazam',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'en-US,en;q=0.9,fr;q=0.8',
	'cookie': cookie,
	'if-none-match': 'W/^\^"2-mZFLkyvTelC5g8XnyQrpOw^\^"'
	}

# Create the URL for the request
URL = "https://www.shazam.com/discovery/v4/en-US/FR/web/-/tag/" + inid + "?limit=50"

# Initialize some values
dict={}
names={}
# To iterate through all shazam tags and create a list of links do the following: Create links dataframe and some way of counting of errors in matching process
links = []
no_links = {}
count = 0 # initialize error count to 0
errcount = 1 # error count for 504 errors to keep track
shaz_50 = []

# Get the last 50 shazam tags :
print("Getting the first 50 shazam tags")
while(shaz_50 == []):
    try:
        print("Attempt number ", errcount)
        shaz_50 = requests.get(URL, headers = headers)
        shaz_50.raise_for_status()
    except requests.exceptions.HTTPError as err:
        errcount = errcount + 1
        shaz_50 = []
        print(err.response.status_code, "error, trying again..")
        pass
print("Success: got the last 50 tags")

# Need them in dataframes to merge them together Get json data for each
print("Try to decode the JSON")
try:
    shaz_50 = shaz_50.json()
except JSONDecodeError:
    print("Error decoding JSON")
print("Success in decoding the JSON")

# Ceck if there are new tagids - import previous ones, and compare with these:
# Import previous tagids that contained all tagids back the csv file into an identical df
previoustagids = pd.read_csv('files/shazam_tagid.csv', index_col=False, header=0)

# Get the 50 latest tagids
shaz_50_tagids = pd.DataFrame(pd.DataFrame(shaz_50)['tags'].tolist())

# This compares the two lengths and put it into the if statement below:
#len(pd.concat([shaz_50_tagids.tagid, previoustagids.tagid]).drop_duplicates(keep="first")) == len(previoustagids.tagid)

# Compare the entire list of previoustagids to shaz_50_tagids
#newtagids = pd.concat([pd.DataFrame(previoustagids.tagid),pd.DataFrame(shazam_df.tagid)]).drop_duplicates(keep=False)
#if not empty, there are new tagids and we want to save this to a file
#if not newtagids.empty:

if (len(pd.concat([shaz_50_tagids.tagid, previoustagids.tagid]).drop_duplicates(keep="first")) == len(previoustagids.tagid)):
    print("No new shazams, exiting..")
    exit()
else:
    # New tags in shazams so lets do the thingy

    # First create a new complete list of tagids
    alltagids = pd.concat([shaz_50_tagids.tagid, previoustagids.tagid]).drop_duplicates(keep="first")

    # Get previous shazam listy thingy
    previous_df = pd.read_csv('files/shazam_df.csv', index_col=False, header=0)

    #Turn the 50 latest tagids into pandas dataframes for the merging
    fifty_df = pd.DataFrame(pd.DataFrame(shaz_50)['tags'].tolist())

    # Create dataframes - new_df is a pandas dataframe with all shazam tags and save in a file for next use
    all_df = pd.concat([fifty_df, previous_df], ignore_index=True, sort=True).drop_duplicates('tagid').reset_index(drop=True)
    all_df.to_csv('files/shazam_tagid.csv', index=False, header=1)

    # Similaryl recreate a file with all tagids
    all_df.tagid.to_csv('files/shazam_tagid.csv', index=False, header=1)

    #Create newtagids which contains only the new tagids
    newtagids = pd.concat([pd.concat([shaz_50_tagids.tagid, previoustagids.tagid]).drop_duplicates(keep="first"), previoustagids.tagid]).drop_duplicates(keep=False)

    #Create newtagids_df which only includes the new tagids
    newtagids_df = all_df.loc[newtagids.eq(all_df['tagid'])]

    # Get tracks
    print("Create shazam_tracks")
    shazam_tracks = pd.DataFrame(newtagids_df['track'].tolist())

    # Get track title and track artist (named "subtitle")
    print("Create shazam headings")
    shazam_headings = pd.DataFrame(shazam_tracks['heading'].tolist())

    # Change subtitle name to artist
    shazam_headings.rename(columns={'subtitle': 'artist'}, inplace=True)

    print("Now going to search deezer for all song titles")
    for i in range(0, len(shazam_headings)):
        print("Searching number", i+1, "Artist:", shazam_headings.artist[i], "Title:", shazam_headings.title[i])
        dict[i] = pd.DataFrame(pd.DataFrame(requests.get("https://api.deezer.com/search/{}/?q={}".format("track", shazam_headings.title[i])).json())['data'].tolist())
        if not dict[i].empty:
            names[i] = pd.DataFrame(pd.DataFrame(dict[i].artist.tolist()).name)
            for j in range(0, len(names[i])):
                names[i].loc[j, 'FR']= fuzz.ratio(shazam_headings.artist[i].lower(), names[i].name[j].lower())
                names[i].loc[j, 'FPR']= fuzz.partial_ratio(shazam_headings.artist[i].lower(), names[i].name[j].lower())
            print("Completed number", i+1)
        else:
            print(shazam_headings.title[i], " did not get any results on Deezer..")
            names[i]=[]
            count = count+1
            no_links[count-1] = [shazam_headings.title[i], shazam_headings.artist[i], "No search results on Deezer"]

    # Loop to get all deezer searches
    # print("Now going to search deezer for all song titles")
    # for i in range(0, len(shazam_headings)):
        # print("Searching number", i+1)
        # dict[i] = pd.DataFrame(requests.get("https://api.deezer.com/search/{}/?q={}".format("track", shazam_headings.title[i])).json())
        # print("Completed number", i+1)

    # Iteration loop
    # for i in range(0, len(shazam_headings)):
        # try:
            # links.append(dict[i].link[pd.DataFrame(dict[i]['artist'].tolist())[pd.DataFrame(dict[i].artist.tolist())['name'] == shazam_headings.artist[i]].index[0]])
        # except:
            # count = count+1
            # print("Could not find artist match for shazam tag ", i, "in deezer - this now makes ", count, "errors total.")
            # no_links[count-1] = [shazam_headings.title[i], shazam_headings.artist[i]]

    for i in range(0, len(shazam_headings)):
        if not pd.DataFrame(names[i]).empty:
            if (names[i]['FR'].max() > 80):
                shazam_headings.loc[i, 'DL_Link'] = dict[i].link[names[i]['FR'].idxmax()]
                links.append(dict[i].link[names[i]['FR'].idxmax()])
            elif (names[i]['FPR'].max() > 80):
                shazam_headings.loc[i, 'DL_Link'] = dict[i].link[names[i]['FPR'].idxmax()]
                links.append(dict[i].link[names[i]['FPR'].idxmax()])
            else:
                count = count+1
                shazam_headings.loc[i, 'DL_Link'] = ("No artist match found..")
                print("Error ", count, "\nCould not match artist for song titled:", shazam_headings.title[i])
                no_links[count-1] = [i, shazam_headings.title[i], shazam_headings.artist[i], "Could not match artist in search results"]


# Future ideas 1. Create database for shazam that stores different data from the shazam tag including the deezer link that was found to match (if any - 
#othereise throw an error and send a telegram message ?) 2. From the shazam database, get list of links to be downloaded since last time - incorporatei 
#into a cron job to automate the process Below line is to compare 2 dataframces and keeping only the ones with differences df_diff = 
#pd.concat([pd.DataFrame(shazam_df.tagid),pd.DataFrame(df2.tagid)]).drop_duplicates(keep=False)
# Get specific tagid that is new df_diff.tagid[0] Below is to write every deezer link that needs to be downloaded
    with open('files/list_to_download', 'w') as f:
        for item in links:
            f.write("%s\n" % item)

    f.close()

# Below is to write every track title and artist that was not able to find a deezer link: First change no_links dict into a list similar to links
    no_links_list = list(no_links.values())

# Then loop for the file
    with open('files/list_cant_find_link', 'a') as g:
        for item in no_links_list:
            g.write("%s\n" % item)

    g.close()
