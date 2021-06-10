# Expects in the same directory the file
# "bgg_links.csv"
# whose second column is consists of links to games on bgg.

# This script:
#    1. Downloads the XML data using the API (if not present already)
#    2. Parses the XML to extract statistics and other details.
#    3. Saves the results to a new CSV.

import xml.sax
import sys, os, csv, glob
import subprocess

class BoardGameHandler(xml.sax.ContentHandler):
    def __init__(self, out_csv):
        self.CurrentData = ""
        self.output_file = out_csv

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "item":
            print("***** Board Game *****")
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
                print(tag, attributes["value"])
                self.name = attributes["value"]
        elif tag == "yearpublished":
            print(tag, attributes["value"])
            self.year = attributes["value"]
        elif tag == "minplayers":
            print(tag, attributes["value"])
            self.minplayers = attributes["value"]
        elif tag == "maxplayers":
            print(tag, attributes["value"])
            self.maxplayers = attributes["value"]
        elif tag == "rank":
            print(tag, attributes["value"])
            self.rank = attributes["value"]
        elif tag == "average":
            print(tag, attributes["value"])
            self.rating = attributes["value"]
        elif tag == "averageweight":
            print(tag, attributes["value"])
            self.weight = attributes["value"]
        elif tag == "owned":
            print(tag, attributes["value"])
            self.owned = attributes["value"]
        elif tag == "usersrated":
            self.user_ratings = attributes["value"]
            print(tag, attributes["value"])
        elif tag == "numcomments":
            self.num_comments = attributes["value"]
            print(tag, attributes["value"])
        elif tag == "link":
            if attributes["type"] == "boardgamedesigner":
                print(attributes["type"], attributes["value"])
                self.designers.append(attributes["value"])
            elif attributes["type"] == "boardgameartist":
                print(attributes["type"], attributes["value"])
                self.artists.append(attributes["value"])
            elif attributes["type"] == "boardgamepublisher":
                print(attributes["type"], attributes["value"])
                self.publishers.append(attributes["value"])

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "item":
            row = [self.id, self.name, self.year, self.rank, self.minplayers, self.maxplayers,
                   self.weight, self.rating, self.user_ratings, self.num_comments]
            with open(self.output_file, "a") as f:
                writer = csv.writer(f)
                writer.writerow(row)
        self.CurrentData = ""

    # Call when a character is read
    def characters(self, content):
        pass

if __name__ == "__main__":
    in_csv = "bgg_links.csv"
    dest = "bgg_files"
    out_csv = "bgg_stats.csv"

    # if the destination folder doesn't exist, create it
    download = True
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
            download = False

    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = BoardGameHandler(out_csv)
    parser.setContentHandler( Handler )


    if download:
        current = os.getcwd()
        prefix = "https://www.boardgamegeek.com/xmlapi2/thing?"
        CNT = 0
        with open(in_csv, "r") as f:
            reader = csv.reader(f)
            reader.__next__() # skip header
            os.chdir(dest)
            for row in reader:
                url = row[1]
                bg_id = url.split("/")[-2]
                bg_id = bg_id.strip()
                # print(bg_id)

                # download the data
                command = "wget"
                arg1 = f"-O {CNT:04}.xml"
                arg2 = prefix + f"id={bg_id}&stats=1"
                result = subprocess.run([command, arg1, arg2])
                if result.returncode:
                    print("Error! Process did not download data correctly.")
                    sys.exit()
                CNT += 1
        os.chdir(current)

    header = ["ID", "Name", "Year", "Rank", "Players (Min)", "Players (Max)",
           "Weight", "Rating", "Number of Ratings", "Number of Comments"]
    with open(out_csv, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    for fname in sorted(glob.glob(dest+"/*.xml")):
        print(fname)
        parser.parse(fname)

