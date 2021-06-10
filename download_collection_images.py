"""
Script to download collection images for a BGG user's collection.

IMPORTANT: You will need to download the data by running the following command in your terminal
    wget http://www.boardgamegeek.com/xmlapi/collection/{BGG_USER}

e.g.) wget http://www.boardgamegeek.com/xmlapi/collection/veronicasalm
More info: https://boardgamegeek.com/wiki/page/BGG_XML_API#

At first, you'll get a message that the data is being generated. Wait a couple minutes and run the
command again - you should get a new output file containing the XML data.

Additional Resources:
    - how to write an xml.sax handler: https://www.tutorialspoint.com/python3/python_xml_processing.htm
    - wget to store an image with the game name as the filename: https://stackoverflow.com/questions/15229294/set-downloaded-filename-in-a-different-directory-using-wget

"""


import xml.sax
import sys, os

class BGGHandler(xml.sax.ContentHandler):
   def __init__(self, dest):
      self.CurrentData = ""
      self.name = ""
      self.thumbnail = ""
      self.dest_dir = dest

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag
      if tag == "item":
          print("***** Board Game *****")

   # Call when an elements ends
   def endElement(self, tag):
      if self.CurrentData == "thumbnail":
          print("Thumbnail URL:", self.thumbnail)

          # extract the extension, e.g., "jpg" or "png"
          extension = self.thumbnail.split(".")[-1]
          # download the images in the destination folder as "dest/game_name.extension"
          command = "wget -c -O {}/{}.{} {}".format(self.dest_dir, self.name.replace(" ", "_"), extension, self.thumbnail)
          # had some issues with the string not formatting correctly, this is overkill but it escapes all the bad characters
          # and does the trick
          # from: https://www.tutorialspoint.com/python3/python_xml_processing.htm
          escaped = command.translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          ".":  r"\.",
                                          "(": r"\(",
                                          ")": r"\)"}))

          # run the command
          os.system(escaped)
      elif self.CurrentData == "name":
          print("Name:", self.name)
      self.CurrentData = ""

   # Call when a character is read
   def characters(self, content):
      if self.CurrentData == "thumbnail":
          self.thumbnail = content
      elif self.CurrentData == "name":
          self.name = content

if ( __name__ == "__main__"):
    # CHANGE ME - bgg_user is the name of the file where the XML data is stored
    #           - destination is the folder where you want the output to go
    bgg_user = "veronicasalm.xml"
    destination = "images"

    # if the destination folder doesn't exist, make it
    if not os.path.isdir(destination):
        print("Creating destination directory...", end=" ")
        os.system("mkdir {}".format(destination))
        print("Done!")
    else:
        print("Destination directory already exists.")

    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = BGGHandler(destination)
    parser.setContentHandler( Handler )

    parser.parse(bgg_user)
