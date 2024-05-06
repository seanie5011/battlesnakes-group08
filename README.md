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
battlesnake play -W 11 -H 11 --name 'Python Starter Project' --url http://localhost:8000 -g solo --browser
```

## Play a Game using Replit

Create a Replit account, either connect up to a GitHub Repo or using the python starter template. Once created, can simply run the code and copy the url on the right hand side. Create a battlesnake with this url and good to go!
