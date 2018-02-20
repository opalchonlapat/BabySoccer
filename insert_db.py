import sqlite3
import pandas as pd
from itertools import cycle

def create_db():
    with sqlite3.connect("database2.sqlite") as con:
        sql_cmd = """
            begin;
            drop table if exists match17;
            create table match17(
              match_id integer primary key ,
              season text,
              stage integer,
              date text,
              home_team_goal integer,
              away_team_goal integer,
              home_team text,
              away_team text
            );
            commit;
        """
        con.executescript(sql_cmd)

def insert_db(list_data):
    try:
        with sqlite3.connect("database2.sqlite") as con:
            sql_cmd = """
              insert into match(match_id, season, stage, date, home_team_goal, away_team_goal, home_team, away_team)
              values(?, ?, ?, ?, ?, ?, ?, ?);
              """
            con.executemany(sql_cmd, list_data)
    except Exception as e:
        print("Error -> {}".format(e))

def insert_db17(list_data):
    try:
        with sqlite3.connect("database2.sqlite") as con:
            sql_cmd = """
              insert into match17(match_id, season, stage, date, home_team_goal, away_team_goal, home_team, away_team)
              values(?, ?, ?, ?, ?, ?, ?, ?);
              """
            con.executemany(sql_cmd, list_data)
    except Exception as e:
        print("Error -> {}".format(e))

def pd_select_db():
    try:
        with sqlite3.connect("database2.sqlite") as con:
            sql_cmd = """
                select * from match
            """
            df = pd.read_sql(sql_cmd, con)
        print(df)
    except Exception as e:
        print("Error -> {}".format(e))

def get_data(data):
    df_2016 = pd.read_csv(data)
    id_list = []
    for id in range(6000, 6000 + len(df_2016)):
        id_list.append(id)
    season = "2016/2017"
    stage = []
    date = []
    home_team_goal = []
    away_team_goal = []
    home_team = []
    away_team = []
    for a in range(len(df_2016)):
        for _ in range(10):
                stage.append(a + 1)
    for df_date in df_2016["Date"]:
        date.append(df_date)
    for df_home_team_goal in df_2016["FTHG"]:
        home_team_goal.append(int(df_home_team_goal))
    for df_away_team_goal in df_2016["FTAG"]:
        away_team_goal.append(int(df_away_team_goal))
    for df_home_team in df_2016["HomeTeam"]:
        home_team.append(df_home_team)
    for df_away_team in df_2016["AwayTeam"]:
        away_team.append(df_away_team)
    for i in range(len(df_2016)):
        data2 = [(id_list[i], season, stage[i], date[i], home_team_goal[i], away_team_goal[i], home_team[i], away_team[i])] # ต้องเป็นทั้ง [()]
        insert_db(data2)
        # print(data2)

def get_data17(data):
    df_2017 = pd.read_csv(data)
    id_list = []
    for id in range(7000, 7000 + len(df_2017)):
        id_list.append(id)
    season = "2017/2018"
    stage = []
    date = []
    home_team_goal = []
    away_team_goal = []
    home_team = []
    away_team = []
    for a in range(len(df_2017)):
        for _ in range(10):
                stage.append(a + 1)
    for df_date in df_2017["Date"]:
        date.append(df_date)
    for df_home_team_goal in df_2017["FTHG"]:
        home_team_goal.append(int(df_home_team_goal))
    for df_away_team_goal in df_2017["FTAG"]:
        away_team_goal.append(int(df_away_team_goal))
    for df_home_team in df_2017["HomeTeam"]:
        home_team.append(df_home_team)
    for df_away_team in df_2017["AwayTeam"]:
        away_team.append(df_away_team)
    for i in range(len(df_2017)):
        data2 = [(id_list[i], season, stage[i], date[i], home_team_goal[i], away_team_goal[i], home_team[i], away_team[i])] # ต้องเป็นทั้ง [()]
        insert_data2(data2)
        # print(data2)

def insert_data2(list_data):
    try:
        with sqlite3.connect('database2.sqlite') as con:
            sql_cmd = """
              insert or ignore into match17(match_id, season, stage, date, home_team_goal, away_team_goal, home_team, away_team)
              values(?, ?, ?, ?, ?, ?, ?, ?);
                      """ # insert or ignore into -> when same value it will skip (ignore) and add new value
            con.executemany(sql_cmd, list_data)
    except Exception as e:
        print("Error -> {}".format(e))

if __name__ == '__main__':
    # create_db()
    # get_data("http://www.football-data.co.uk/mmz4281/1617/E0.csv")
    get_data17('http://www.football-data.co.uk/mmz4281/1718/E0.csv')
    # pd_select_db()
    # date_list = []
    # with sqlite3.connect('database2.sqlite') as con:
    #     matches_data_16 = pd.read_sql('select * from match;', con)
    # matches_df = pd.DataFrame(matches_data_16)
    # matches_df['date'] = pd.to_datetime(matches_df['date'])
    # for date in range(42595, 42595 + len(matches_df), 7):
    #     for _ in range(10):
    #         date_list.append(date)
    # print(date_list)

