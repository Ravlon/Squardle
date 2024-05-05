import requests
# import json

URL = "https://squaredle.app/api/index.php"
KEYS = ["op","args"]
OP = "getLeaderboardScores"
ARGS = ["puzzleID","showDebug","favorites","isBetaPuzzle","lastScore","getCompletedPercentiles","uuid","game"]

def get_leaderboard(**kwargs):
    """Return JSON response from the api.
    Give following paramenters: ["puzzleID","showDebug","favorites","isBetaPuzzle","lastScore","getCompletedPercentiles","uuid","game"]
    """
    args = {k:kwargs[k] for k in ARGS if k in kwargs}
    if all(k in kwargs for k in ARGS):
        dict_data = {KEYS[1]:OP,KEYS[2]:args}
        response = requests.post(URL, json=dict_data,timeout=100)
    else:
        raise ReferenceError
    if response.ok:
        return response.json()
    response.raise_for_status()
    
