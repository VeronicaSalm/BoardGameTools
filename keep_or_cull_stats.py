"""
keep_or_cull_stats.py

Can be run after deep_game_stats.py, but is specialized to my
Keep or Cull spreadsheet. This is a CSV called "Keep_or_Cull_Links.csv"
and contiains the following six columns, in order:
    Game: the name of the board game
    Link: the BGG link
    Week: the week of the Keep or Cull episode
    Johannes: whether Johannes wanted to keep or cull the game
    Sunniva: same, but Sunniva's opinion
    Verdict: whether they ultimately decided to keep or cull the game

This script analyzes the output JSON file and compiles some interesting
statistics for the games overall, games kept, and games culled.
"""

# TODO: add command line argument parsing
# TODO: write README with running instructions and summary
import os, csv, json, sys
from collections import defaultdict
from settings import DEBUG, ID, NAME, YEAR, RANK, MIN_PLAYERS, MAX_PLAYERS, \
                     COMPLEXITY, RATING, NUM_RATINGS, NUM_COMMENTS, DESIGNERS, \
                     PUBLISHERS, ARTISTS, WEEK, P1, P2, VERDICT, KEEP, CULL, GAMES_LIST

def create_dest_dir(dest):
    """
    Ensures that the destination directory [dest] (where output
    will be stored) exists and is either empty or the user confirms
    that any existing files should not be deleted.
    """
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
            print("Okay. Will not delete old files.")

if __name__ == "__main__":
    in_csv = "Keep_or_Cull_Links.csv"
    in_json = "bgg_stats.json"
    general_out_file = "general.csv"
    publisher_file = "publishers.csv"
    artist_file = "artists.csv"
    designer_file = "designers.csv"

    DEST_DIR = "output"
    PUBLISHER_FPATH = os.path.join(DEST_DIR, publisher_file)
    ARTIST_FPATH = os.path.join(DEST_DIR, artist_file)
    DESIGNER_FPATH = os.path.join(DEST_DIR, designer_file)
    GENERAL_FPATH = os.path.join(DEST_DIR, general_out_file)


    create_dest_dir(DEST_DIR)

    # Read the downloaded stats json file.
    games = dict()
    with open(in_json, "r") as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            bg_id = str(data[ID])
            games[bg_id] = data
    print(f"Loaded {len(games)} board games.")

    # Read the Keep or Cull spreadsheet.
    # Add the Keep or Cull info to the game objects.
    publishers = dict() # counter for publishers
    artists = dict() # counter for artists
    designers = dict() # counter for designers
    agg = {KEEP : dict(), CULL : dict()} # aggregate stats for keep vs cull
    agg[KEEP] = defaultdict(list)
    agg[CULL] = defaultdict(list)
    fields = [COMPLEXITY, RATING, RANK, NUM_RATINGS, NUM_COMMENTS, YEAR]

    with open(in_csv, "r") as f:
        reader = csv.reader(f)
        reader.__next__() # skip header
        for row in reader:
            url = row[1]
            bg_id = url.split("/")[-2]
            bg_id = str(bg_id.strip())

            games[bg_id][WEEK] = int(row[2])
            games[bg_id][P1] = row[3]
            games[bg_id][P2] = row[4]
            games[bg_id][VERDICT] = row[5]

            name = games[bg_id][NAME]

            if games[bg_id][VERDICT] == KEEP:
                name += " (KEEP)"
            else:
                name += " (CULL)"

            ### PUBLISHERS ###
            p = games[bg_id][PUBLISHERS][0] # only use the first publisher, usually the English one
            if p not in publishers:
                publishers[p] = {KEEP: 0, CULL: 0, GAMES_LIST: []}
            verdict = games[bg_id][VERDICT]
            publishers[p][verdict] += 1
            publishers[p][GAMES_LIST].append(name)


            ### ARTISTS ###
            for a in games[bg_id][ARTISTS]:
                if a not in artists:
                    artists[a] = {KEEP: 0, CULL: 0, GAMES_LIST: []}
                verdict = games[bg_id][VERDICT]
                artists[a][verdict] += 1
                artists[a][GAMES_LIST].append(name)

            ### DESIGNERS ###
            for d in games[bg_id][DESIGNERS]:
                if d not in designers:
                    designers[d] = {KEEP: 0, CULL: 0, GAMES_LIST: []}
                verdict = games[bg_id][VERDICT]
                designers[d][verdict] += 1
                designers[d][GAMES_LIST].append(name)

            ### OTHER ###
            for field in fields:
                agg[verdict][field].append(games[bg_id][field])

    # sort first by total number of games, then by largest difference between keep and cull
    pubs = list(sorted(publishers.items(), key=lambda x: (x[1][KEEP]+x[1][CULL], x[1][KEEP]-x[1][CULL]), reverse=True))
    artists_sorted = list(sorted(artists.items(), key=lambda x: (x[1][KEEP]+x[1][CULL], x[1][KEEP]-x[1][CULL]), reverse=True))
    designers_sorted = list(sorted(designers.items(), key=lambda x: (x[1][KEEP]+x[1][CULL], x[1][KEEP]-x[1][CULL]), reverse=True))

    # write the output to CSV
    with open(DESIGNER_FPATH, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Designer", "# Keep", "# Cull", "Total Games by This Designer", "Games"])

        for p, d in designers_sorted:
            games = "\n".join(sorted(d[GAMES_LIST]))
            writer.writerow([p, d[KEEP], d[CULL], d[KEEP]+d[CULL], games])

    with open(ARTIST_FPATH, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Artist", "# Keep", "# Cull", "Total Games by This Artist", "Games"])

        for a, d in artists_sorted:
            games = "\n".join(sorted(d[GAMES_LIST]))
            writer.writerow([a, d[KEEP], d[CULL], d[KEEP]+d[CULL], games])

    with open(PUBLISHER_FPATH, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Publisher", "# Keep", "# Cull", "Total Games by This Publisher", "Games"])

        for p, d in pubs:
            games = "\n".join(sorted(d[GAMES_LIST]))
            writer.writerow([p, d[KEEP], d[CULL], d[KEEP]+d[CULL], games])

    for verdict in [KEEP, CULL]:
        print(verdict)
        for field in [COMPLEXITY, RATING, RANK, YEAR, NUM_COMMENTS, NUM_RATINGS]:
            L = [f for f in agg[verdict][field] if type(f) != str]
            print("    -", field, sum(L) / len(L))
