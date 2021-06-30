# Expects in the same directory the file
# "bgg_links.csv"
# whose second column is consists of links to games on bgg.

# This script:
#    1. Downloads the XML data using the API (if not present already)
#    2. Parses the XML to extract statistics and other details.
#    3. Saves the results to a new JSON file, one game per line.

import xml.sax
import sys, os, csv, glob, json
import subprocess
from settings import DEBUG, ID, NAME, YEAR, RANK, MIN_PLAYERS, MAX_PLAYERS, \
                     COMPLEXITY, RATING, NUM_RATINGS, NUM_COMMENTS, DESIGNERS, \
                     PUBLISHERS, ARTISTS

class BoardGameHandler(xml.sax.ContentHandler):
    def __init__(self, out_file):
        self.CurrentData = ""
        self.output_file = out_file

        self.stored = set()
        if os.path.exists(self.output_file):
            with open(self.output_file, "r") as fobj:
                lines = fobj.readlines()
                for line in lines:
                    data = json.loads(line)
                    self.stored.add(data[ID])

            print("Already processed:", self.stored)


    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "item":
            if DEBUG: print("***** Board Game *****")
            self.id = attributes["id"]
            self.name = ""
            self.year = ""
            self.minplayers = ""
            self.maxplayers = ""
            self.rank = ""
            self.rating = ""
            self.weight = ""
            self.user_ratings = ""
            self.num_comments = ""
            self.designers = []
            self.artists = []
            self.publishers = []
        elif tag == "name":
            if attributes["type"] == "primary":
                if DEBUG: print(tag, attributes["value"])
                self.name = attributes["value"]
        elif tag == "yearpublished":
            if DEBUG: print(tag, attributes["value"])
            self.year = attributes["value"]
        elif tag == "minplayers":
            if DEBUG: print(tag, attributes["value"])
            self.minplayers = attributes["value"]
        elif tag == "maxplayers":
            if DEBUG: print(tag, attributes["value"])
            self.maxplayers = attributes["value"]
        elif tag == "rank":
            if DEBUG: print(tag, attributes["value"])
            self.rank = attributes["value"]
        elif tag == "average":
            if DEBUG: print(tag, attributes["value"])
            self.rating = attributes["value"]
        elif tag == "averageweight":
            if DEBUG: print(tag, attributes["value"])
            self.weight = attributes["value"]
        elif tag == "owned":
            if DEBUG: print(tag, attributes["value"])
            self.owned = attributes["value"]
        elif tag == "usersrated":
            self.user_ratings = attributes["value"]
            if DEBUG: print(tag, attributes["value"])
        elif tag == "numcomments":
            self.num_comments = attributes["value"]
            if DEBUG: print(tag, attributes["value"])
        elif tag == "link":
            if attributes["type"] == "boardgamedesigner":
                if DEBUG: print(attributes["type"], attributes["value"])
                self.designers.append(attributes["value"])
            elif attributes["type"] == "boardgameartist":
                if DEBUG: print(attributes["type"], attributes["value"])
                self.artists.append(attributes["value"])
            elif attributes["type"] == "boardgamepublisher":
                if DEBUG: print(attributes["type"], attributes["value"])
                self.publishers.append(attributes["value"])

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "item":
            #  row = [self.id, self.name, self.year, self.rank, self.minplayers, self.maxplayers,
                   #  self.weight, self.rating, self.user_ratings, self.num_comments, self.artists, self.designers, self.publishers]
            if self.id not in self.stored:
                try:
                    self.rank = int(self.rank)
                except ValueError:
                    self.rank = self.rank
                game = { ID : self.id,
                         NAME : self.name,
                         YEAR : int(self.year),
                         RANK : self.rank,
                         MIN_PLAYERS : int(self.minplayers),
                         MAX_PLAYERS : int(self.maxplayers),
                         COMPLEXITY : float(self.weight),
                         RATING : float(self.rating),
                         NUM_RATINGS : int(self.user_ratings),
                         NUM_COMMENTS : int(self.num_comments),
                         DESIGNERS : self.designers,
                         PUBLISHERS : self.publishers,
                         ARTISTS : self.artists
                       }
                with open(self.output_file, "a") as f:
                    print(json.dumps(game), file=f)
        self.CurrentData = ""

    # Call when a character is read
    def characters(self, content):
        pass

if __name__ == "__main__":
    in_csv = "Keep_or_Cull_Links.csv"
    dest = "bgg_files"
    out_file = "bgg_stats.json"

    # if the destination folder doesn't exist, create it
    if not os.path.isdir(dest):
        print("Creating destination directory...", end=" ")
        os.system("mkdir {}".format(dest))
        print("Done!")
    else:
        # otherwise quit
        r = input("Destination directory already exists. Would you like to remove it?: ")
        if r.lower().startswith("y"):
            print("Removing old directory... ")
            os.system(f"rm -r {dest}")
            print("Creating new destination directory...", end=" ")
            os.system("mkdir {}".format(dest))
            print("Done!")
        else:
            print("Okay. Will not overwrite old files.")

    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = BoardGameHandler(out_file)
    parser.setContentHandler( Handler )

    current = os.getcwd()
    prefix = "https://www.boardgamegeek.com/xmlapi2/thing?"
    CNT = 0
    download = True
    with open(in_csv, "r") as f:
        reader = csv.reader(f)
        reader.__next__() # skip header
        os.chdir(dest)
        for row in reader:
            url = row[1]
            bg_id = url.split("/")[-2]
            bg_id = bg_id.strip()

            if not download:
                # If we got an error, skip downloading all future files
                # Most likely, this was an API limit issue
                continue

            if os.path.exists(f"{bg_id}.xml"):
                # avoid downloading a game we already have
                print(f"Skipping {bg_id}, file already exists...")
                continue

            # download the data
            command = "wget"
            arg1 = f"-O{bg_id}.xml"
            arg2 = prefix + f"id={bg_id}&stats=1"
            result = subprocess.run([command, arg1, arg2])
            if result.returncode:
                print("Error! Process did not download data correctly.")
                os.system(f"rm {bg_id}.xml")
                download = False
            else:
                CNT += 1
    os.chdir(current)

    for fname in sorted(glob.glob(dest+"/*.xml")):
        print(fname)
        parser.parse(fname)

