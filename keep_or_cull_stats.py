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
import csv, json, sys
from collections import defaultdict
from settings import DEBUG, ID, NAME, YEAR, RANK, MIN_PLAYERS, MAX_PLAYERS, \
                     COMPLEXITY, RATING, NUM_RATINGS, NUM_COMMENTS, DESIGNERS, \
                     PUBLISHERS, ARTISTS, WEEK, P1, P2, VERDICT, KEEP, CULL

if __name__ == "__main__":
    in_csv = "Keep_or_Cull_Links.csv"
    in_json = "bgg_stats.json"
    out_file = "keep_or_cull_stats.json"

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

            ### PUBLISHERS ###
            p = games[bg_id][PUBLISHERS][0] # only use the first publisher, usually the English one
            if p not in publishers:
                publishers[p] = defaultdict(int)
            verdict = games[bg_id][VERDICT]
            publishers[p][verdict] += 1

            ### ARTISTS ###
            for a in games[bg_id][ARTISTS]:
                if a not in artists:
                    artists[a] = defaultdict(int)
                verdict = games[bg_id][VERDICT]
                artists[a][verdict] += 1

            ### DESIGNERS ###
            for d in games[bg_id][DESIGNERS]:
                if d not in designers:
                    designers[d] = defaultdict(int)
                verdict = games[bg_id][VERDICT]
                designers[d][verdict] += 1

            ### OTHER ###
            for field in fields:
                agg[verdict][field].append(games[bg_id][field])

    pubs = list(sorted(publishers.items(), key=lambda x: x[1][KEEP], reverse=True))
    artists_sorted = list(sorted(artists.items(), key=lambda x: (x[1][CULL]-x[1][KEEP], x[1][CULL]), reverse=True))
    designers_sorted = list(sorted(designers.items(), key=lambda x: (x[1][KEEP]-x[1][CULL], x[1][KEEP]), reverse=True))
    cnt = 0
    for p, d in designers_sorted:
        print(p, KEEP, d[KEEP], CULL, d[CULL])
        cnt += 1
        if cnt == 5:
            break

    for verdict in [KEEP, CULL]:
        print(verdict)
        for field in fields:
            L = [f for f in agg[verdict][field] if type(f) != str]
            print("    -", field, sum(L) / len(L))
