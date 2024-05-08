# Battlesnake for DD2438 Group 8

Group 8s code for Battlesnake written in Python. 

Get started at [play.battlesnake.com](https://play.battlesnake.com).

See the [Battlesnake API Docs](https://docs.battlesnake.com/api) for more detail. 

## Technologies Used

This project uses [Python 3](https://www.python.org/) and [Flask](https://flask.palletsprojects.com/).

## Run Battlesnake

Install dependencies using pip

```sh
pip install -r requirements.txt
```

Start the Battlesnake

```sh
python main.py
```

You should see the following output once it is running

```sh
Running your Battlesnake at http://0.0.0.0:8000
 * Serving Flask app 'My Battlesnake'
 * Debug mode: off
```

Open [localhost:8000](http://localhost:8000) in your browser and you should see the output of the json file for our snake, for example:

```json
{"apiversion":"1","author":"","color":"#888888","head":"default","tail":"default"}
```

## Play a Game Locally

Install the [Battlesnake CLI](https://github.com/BattlesnakeOfficial/rules/tree/main/cli), we used version `1.2.3` on Windows `x86_64`. 

Command to run a local game

```sh
battlesnake play -W 11 -H 11 --name SORZWE --url http://localhost:8000 -g solo --browser
```

Example output of the `main.py` would then be:

```
{'game': {'id': '8eb55f8b-0b3f-4a32-9721-7ec66d9624c5', 'ruleset': {'name': 'solo', 'version': 'cli', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 14, 'hazardMap': '', 'hazardMapAuthor': '', 'royale': {'shrinkEveryNTurns': 25}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'map': 'standard', 'timeout': 500, 'source': ''}, 'turn': 9, 'board': {'height': 11, 'width': 11, 'snakes': [{'id': 'e78dbe31-941e-47dc-8448-509d4b7a74e4', 'name': 'SORZWE', 'latency': '314', 'health': 99, 'body': [{'x': 5, 'y': 4}, {'x': 5, 'y': 5}, {'x': 6, 'y': 5}, {'x': 6, 'y': 6}, {'x': 6, 'y': 7}], 'head': {'x': 5, 'y': 4}, 'length': 5, 'shout': '', 'squad': '', 'customizations': {'color': '#00E4FF', 'head': 'smart-caterpillar', 'tail': 'weight'}}], 'food': [{'x': 2, 'y': 0}], 'hazards': []}, 'you': {'id': 'e78dbe31-941e-47dc-8448-509d4b7a74e4', 'name': 'SORZWE', 'latency': '0', 'health': 99, 'body': [{'x': 5, 'y': 4}, {'x': 5, 'y': 5}, {'x': 6, 'y': 5}, {'x': 6, 'y': 6}, {'x': 6, 'y': 7}], 'head': {'x': 5, 'y': 4}, 'length': 5, 'shout': '', 'squad': '', 'customizations': {'color': '#00E4FF', 'head': 'smart-caterpillar', 'tail': 'weight'}}}
```

## Play a Game using Replit

Create a Replit account, either connect up to a GitHub Repo or using the python starter template. Once created, can simply run the code and copy the url on the right hand side. Create a battlesnake with this url and good to go!
