import pandas as pd
from collections import OrderedDict
import json
import requests
from datetime import date, datetime
import sqlite3
from bs4 import BeautifulSoup
from itertools import islice


def get_match_score_data(data, start_season, end_season, past_stage):
    con = sqlite3.connect('database2.sqlite')
    sql = f'''
        select max(match_id)
        from {database}
    '''
    last_match_id_df = pd.read_sql(sql, con)
    last_match_id = last_match_id_df.iat[0, 0]

    if past_stage == 38:
        last_match_id = last_match_id + 1
        print(last_match_id)
    else:
        last_match_id = past_matches.loc[(past_matches['season'] == season_url)].match_id.min()
        print(last_match_id)

    df_2017 = pd.read_csv(data)
    df_2017.dropna(inplace=True, subset=['FTHG', 'FTAG'])
    id_list = []
    for id in range(last_match_id, last_match_id + len(df_2017) + 1):
        id_list.append(id)
    season = f"{start_season}/{end_season}"
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
        data2 = [(id_list[i], season, stage[i], date[i], home_team_goal[i], away_team_goal[i], home_team[i],
                  away_team[i])]  # ต้องเป็นทั้ง [()]
        insert_match_score_data(data2)


def insert_match_score_data(list_data):
    with sqlite3.connect('database2.sqlite') as con:
        sql_cmd = """
            insert or ignore into match(match_id, season, stage, date, home_team_goal, away_team_goal, home_team, away_team)
            values(?,?,?,?,?,?,?,?);
        """
        con.executemany(sql_cmd, list_data)

def change_team_name(n):
    if n == 'Manchester Utd':
        return 'Manchester United'
    elif n == 'Spurs':
        return 'Tottenham Hotspur'
    elif n == 'Newcastle Utd':
        return 'Newcastle United'
    elif n == 'QPR':
        return 'Queens Park Rangers'
    elif n == 'West Ham':
        return 'West Ham United'
    elif n == 'West Brom':
        return 'West Bromwich Albion'
    elif n == 'Norwich':
        return 'Norwich City'
    else:
        return n


if __name__ == '__main__':
    # get past stage from match db
    database = 'match'
    with sqlite3.connect('database2.sqlite') as con:
        past_matches = pd.read_sql(f'select * from {database}', con)
    past_stage = int(past_matches.iat[-1, 2])
    season_url = past_matches.iat[-1, 1]
    start_season = f'{int(season_url[:4])+1}'
    end_season = f'{int(season_url[5:])+1}'

    if past_stage == 38:

        # get match schedule
        try:
            url = f'https://raw.githubusercontent.com/opendatajson/football.json/master/{start_season}-{end_season[2:]}/en.1.json'
            r = requests.get(url)
            r.text
            j = json.loads(r.text, object_pairs_hook=OrderedDict)
            j2 = pd.io.json.loads(r.text)
            df3 = pd.DataFrame()
            for i in range(38):
                df2 = pd.DataFrame(j2['rounds'][i]['matches'])
                df3 = df3.append(df2, ignore_index=True)
            df3.fillna(0, axis=1, inplace=True)
            df3['team1'] = df3.team1.map(lambda s: s['name'])
            df3['team2'] = df3.team2.map(lambda s: s['name'])
            date = []
            for i, r in df3.iterrows():
                date.append(df3.iloc[i]['date'])
            date2 = []
            for d in date:
                date2.append(datetime.strptime(d, "%Y-%m-%d").date().strftime('%d/%m/%y'))
            df_date = pd.DataFrame({'date': date2})
            df3['season'] = f'{start_season}/{end_season}'
            stage = []
            for a in range(len(df3) // 10):
                for _ in range(10):
                    stage.append(a + 1)
            df_stage = pd.DataFrame({'stage': stage})
            df3['stage'] = df_stage['stage']
            df3['date'] = df_date['date']
            df3.columns = ['date', 'home_team_goal', 'away_team_goal', 'home_team', 'away_team', 'season', 'stage']
            df3.drop(['home_team_goal', 'away_team_goal'], axis=1, inplace=True)
            with sqlite3.connect('database2.sqlite') as con:
                df3.to_sql('match_schedule', con, if_exists='append', index=False)

            # get matches
            try:
                link_match = f'http://www.football-data.co.uk/mmz4281/{start_season[2:]}{end_season[2:]}/E0.csv'
                get_match_score_data(link_match, start_season, end_season, past_stage)
            except Exception as e:
                pass

        except Exception as e:
            print('Not matches schedule yet')

    else:
        # get matches
        try:
            link_match = f'http://www.football-data.co.uk/mmz4281/{int(start_season[2:])-1}{int(end_season[2:])-1}/E0.csv'
            get_match_score_data(link_match, int(start_season) - 1, int(end_season) - 1, past_stage)
        except Exception as e:
            print("Not matches yet")

    # get team rating
    # https://www.fifaindex.com/teams/?league=13

    # get current season data from website
    url = 'https://www.fifaindex.com/teams/?league=13'
    r = requests.get(url)
    s = BeautifulSoup(r.text, 'lxml')
    d = s.find('ol', {'class': 'breadcrumb'})
    ol_tag = d.find_all('li')

    # check season from website
    season_prefix = ol_tag[1].find('a').get_text()
    season_prefix_int = int(season_prefix[5:7])

    # chech season from db
    with sqlite3.connect('database2.sqlite') as con:
        sql_cmd = '''
            select season
            from team_rating
            order by team_rating_id desc limit 1
        '''
        season_df = pd.read_sql(sql_cmd, con)
    last_season = season_df.iat[0, 0]
    start_season = int(last_season[:4])
    end_season = int(last_season[5:])
    end_season_prefix = int(last_season[7:])

    # if on website has new season, add new team rating data.
    if end_season_prefix != season_prefix_int:
        start_season += 1
        end_season += 1
        season = f'{start_season}/{end_season}'
        print(end_season_prefix)
        print(season_prefix_int)

        d_rating = s.find('div', {'id': 'no-more-tables'})
        a_tags = d_rating.find_all('a')
        span_tags = d_rating.find_all('span')

        team_rating = []
        season = '2017/2018'
        # span : เริ่ม 0:ATT , 1:MID , 2 : DEF , 3:OVR
        for a, s, s2, s3, s4 in zip(islice(a_tags, 4, None, 3), islice(span_tags, 0, None, 5),
                                    islice(span_tags, 1, None, 5), islice(span_tags, 2, None, 5),
                                    islice(span_tags, 3, None, 5)):
            team_name = a['title']
            span_value = s.contents[0]
            span_value2 = s2.contents[0]
            span_value3 = s3.contents[0]
            span_value4 = s4.contents[0]
            team_rating.append(
                (season, team_name, int(span_value), int(span_value2), int(span_value3), int(span_value4)))
        team_rating = [team_rating]  # tuple of list for append to DF
        team_rating

        df = pd.DataFrame()

        for i, d in enumerate(team_rating):
            df = df.append(team_rating[i])
        df.columns = ['season', 'team_name', 'attack_rating', 'midfield_rating', 'defence_rating', 'team_rating']
        df

        df['team_name'] = df['team_name'].map(lambda n: change_team_name(n))
        df

        with sqlite3.connect('database2.sqlite') as con:
            df.to_sql('team_rating_test', con, if_exists='append', index=False)
