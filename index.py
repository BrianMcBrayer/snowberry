import os
from dotenv import load_dotenv
from pydantic import BaseModel
import csv

load_dotenv()
CFBD_API_KEY = os.getenv("CFBD_API_KEY")

import cfbd
from cfbd.models import Game
from cfbd.rest import ApiException

class GameDTO(BaseModel):
    season: int
    week: int
    season_type: str
    start_date: str
    completed: bool
    venue: str | None
    team1: str
    team1_points: int
    team2: str
    team2_points: int
    winning_team: str | None

configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))
year = 2024 # int | Year/season filter for games
# season_type = 'regular' # str | Season type filter (regular or postseason) (optional) (default to regular)
division = 'fbs' # str | Division classification filter (fbs/fcs/ii/iii) (optional)

def json_to_csv(json_data: list[GameDTO], csv_filename):
    # Define the headers of the CSV
    headers = [
        "week",
        "team1",
        "team2",
        "winning_team",
        "season",
        "season_type",
        "start_date",
        "completed",
        "venue",
        "team1_points",
        "team2_points"
    ]

    # Open the file to write CSV data
    # overwrite the existing file
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write the header
        writer.writeheader()
        
        # Write the rows of data
        for game in json_data:
            game_dict = game.model_dump()
            
            # Write the game data as a row in CSV
            writer.writerow(game_dict)

try:
    # Games and results
    api_response: list[Game] = games_api.get_games(year=year, division=division)
    # post_season_api_response: list[Game] = games_api.get_games(year=year, division=division, season_type='postseason')

    # convert api_response to GameDTO list
    game_dtos: list[GameDTO] = []
    for game in api_response:
        if game.completed is not True:
            continue
        
        winning_team = game.home_team if game.home_points > game.away_points else game.away_team

        game_dto = GameDTO(
            season=game.season,
            week=game.week,
            season_type=game.season_type,
            start_date=game.start_date,
            completed=game.completed,
            venue=game.venue,
            team1=game.home_team,
            team1_points=game.home_points,
            team2=game.away_team,
            team2_points=game.away_points,
            winning_team= winning_team
        )

        game_dtos.append(game_dto)

    # for game in post_season_api_response:
    #     if game.completed is not True:
    #         continue
        
    #     winning_team = game.home_team if game.home_points > game.away_points else game.away_team

    #     game_dto = GameDTO(
    #         season=game.season,
    #         week=game.week,
    #         season_type=game.season_type,
    #         start_date=game.start_date,
    #         completed=game.completed,
    #         venue=game.venue,
    #         team1=game.home_team,
    #         team1_points=game.home_points,
    #         team2=game.away_team,
    #         team2_points=game.away_points,
    #         winning_team= winning_team
    #     )

    #     game_dtos.append(game_dto)

    json_to_csv(game_dtos, 'games.csv')
except ApiException as e:
    print("Exception when calling GamesApi->get_games: %s\n" % e)

    