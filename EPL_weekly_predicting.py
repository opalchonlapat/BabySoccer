# --In[1]--
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import sqlite3
from IPython.display import display, clear_output
from sklearn.naive_bayes import MultinomialNB
# from subprocess import check_output
from datetime import date, datetime
# print(check_output("").decode("utf8"))

# --In[5]--
# State the result as home or away win/draw/lose - 6 possibilities
# Create a binary result
def determine_result(match_list):
    match_list["home_win"] = np.where(match_list["home_team_goal"] > match_list["away_team_goal"], 1, 0) # สร้าง column ใหม่ตามเงื่อนไข ถ้าใช่ให้เป็น 1 ไม่ใช่เป็น 0
    match_list["home_draw"] = np.where(match_list["home_team_goal"] == match_list["away_team_goal"], 1, 0)
    match_list["home_lose"] = np.where(match_list["home_team_goal"] < match_list["away_team_goal"], 1, 0)
    match_list["away_win"] = np.where(match_list["home_team_goal"] < match_list["away_team_goal"], 1, 0)
    match_list["away_draw"] = np.where(match_list["home_team_goal"] == match_list["away_team_goal"], 1, 0)
    match_list["away_lose"] = np.where(match_list["home_team_goal"] > match_list["away_team_goal"], 1, 0)

# --In[10]--
# Get the target results for training
# Function to determine whether result is a win/draw/lose
def determine_home_result(match):
    if match['home_team_goal'] > match['away_team_goal']:
        return 'win'
    elif match['home_team_goal'] < match['away_team_goal']:
        return 'lose'
    else:
        return 'draw'

# --In[13]--
# Function to determine whether the highest prediction is for win/draw/lose
def predict_home_result(match):
    if (match['win'] >= match['draw']) & (match['win'] >= match['lose']):
        return 'win' # Favour a home win if probability equal
    elif (match['lose'] > match['win']) & (match['lose'] > match['draw']):
        return 'lose'
    else:
        return 'draw'

def convert_date_to_code16(matches_data_16):
    date = []
    for i in matches_data_16['date']:
        date.append(i)

    x = date[0]
    d = datetime.strptime(x, "%d/%m/%y").date()
    dict2 = {}
    base = 42595
    for i in date:
        date_l = datetime.strptime(i, "%d/%m/%y").date()
        date_dif = date_l - d
        dict2[date_l] = str(base + date_dif.days)
    t = []
    for i in range(len(date)):
        t.append(dict2[datetime.strptime(date[i], '%d/%m/%y').date()])
    matches_data_16['date'] = list(map((lambda i: t[i]), range(len(t))))
    return matches_data_16

def convert_date_to_code17(matches_data_17):
    stage = []
    for i in matches_data_17['stage']:
        stage.append(i)
    date = []
    for i in matches_data_17['date']:
        date.append(i)
    dict_date = {}
    for i, j in zip(stage, date):
        dict_date[i] = datetime.strptime(j, "%d/%m/%y").date()
    dict2 = {}
    base = 42959
    for i in stage:
        if i == 1:
            dict2[i] = base
        else:
            date_dif = dict_date[i] - dict_date[i - 1]
            if date_dif.days < 14:
                dict2[i] = dict2[i - 1] + 7
            if date_dif.days >= 14:
                dict2[i] = dict2[i - 1] + 14
    t = []
    for i in stage:
        t.append(str(dict2[i]))
    matches_data_17['date'] = list(map((lambda i: t[i]), range(len(t))))
    return matches_data_17


def convert_team_name(last_season):
    for index, row in last_season.iterrows():
        if row['home_team'] == 'Man United':
            last_season.loc[index, 'home_team'] = 'Manchester United'
        if row['home_team'] == 'Man City':
            last_season.loc[index, 'home_team'] = 'Manchester City'
        if row['home_team'] == 'Leicester':
            last_season.loc[index, 'home_team'] = 'Leicester City'
        if row['home_team'] == 'West Brom':
            last_season.loc[index, 'home_team'] = 'West Bromwich Albion'
        if row['home_team'] == 'Newcastle':
            last_season.loc[index, 'home_team'] = 'Newcastle United'
        if row['home_team'] == 'Stoke':
            last_season.loc[index, 'home_team'] = 'Stoke City'
        if row['home_team'] == 'Swansea':
            last_season.loc[index, 'home_team'] = 'Swansea City'
        if row['home_team'] == 'West Ham':
            last_season.loc[index, 'home_team'] = 'West Ham United'
        if row['home_team'] == 'Tottenham':
            last_season.loc[index, 'home_team'] = 'Tottenham Hotspur'
        if row['home_team'] == 'Hull':
            last_season.loc[index, 'home_team'] = 'Hull City'

        if row['away_team'] == 'Man United':
            last_season.loc[index, 'away_team'] = 'Manchester United'
        if row['away_team'] == 'Man City':
            last_season.loc[index, 'away_team'] = 'Manchester City'
        if row['away_team'] == 'Leicester':
            last_season.loc[index, 'away_team'] = 'Leicester City'
        if row['away_team'] == 'West Brom':
            last_season.loc[index, 'away_team'] = 'West Bromwich Albion'
        if row['away_team'] == 'Newcastle':
            last_season.loc[index, 'away_team'] = 'Newcastle United'
        if row['away_team'] == 'Stoke':
            last_season.loc[index, 'away_team'] = 'Stoke City'
        if row['away_team'] == 'Swansea':
            last_season.loc[index, 'away_team'] = 'Swansea City'
        if row['away_team'] == 'West Ham':
            last_season.loc[index, 'away_team'] = 'West Ham United'
        if row['away_team'] == 'Tottenham':
            last_season.loc[index, 'away_team'] = 'Tottenham Hotspur'
        if row['away_team'] == 'Hull':
            last_season.loc[index, 'away_team'] = 'Hull City'
    return last_season

if __name__ == '__main__':
    this_season = "2017/2018"

    with sqlite3.connect("database.sqlite") as engine:
        matches = pd.read_sql_query("select * from match where League_id = 1729;", engine)
    matches = matches[matches.columns[:11]] # get first 11 column data
    teams = pd.read_sql_query("select * from team;", engine)
    # Add team names & tidy up
    matches = pd.merge(left=matches, right=teams, how="left", left_on="home_team_api_id", right_on="team_api_id") # เอาข้อมูลจากตาราง team ทั้งหมดมาใส่ใน matches ของ home team
    matches = matches.drop(["country_id", "league_id", "home_team_api_id", "id_y", "team_api_id", "team_short_name"], axis=1) # ลบ column ที่ไม่จำเป็นทิ้งไป
    matches.rename(columns={"id_x":"match_id", "team_long_name":"home_team"}, inplace=True) # เปลี่ยนชื่อ column และแทนที่ลงตัวแปรเดิมเลย
    matches = pd.merge(left=matches, right=teams, how="left", left_on="away_team_api_id", right_on="team_api_id")
    matches = matches.drop(["id", "match_api_id", "away_team_api_id", "team_api_id", "team_short_name"], axis=1)
    matches.rename(columns={"id_x":"match_id", "team_long_name":"away_team"}, inplace=True)
    # print(matches.tail())

    # --In[4]--
    # Add in this season(16/17) matches - need to convert to csv at some point
    with sqlite3.connect('database2.sqlite') as con:
        matches_data_16 = pd.read_sql('select * from match;', con)
        matches_data_17 = pd.read_sql('select * from match17;', con)
        matches_schedule = pd.read_sql('select * from match_schedule3;', con)
    # matches_data_16['date'] = pd.to_datetime(matches_data_16['date'])

    convert_date_to_code16(matches_data_16)
    convert_date_to_code17(matches_data_17)
    matches_schedule = convert_date_to_code17(matches_schedule)
    this_week = int(matches_data_17[-1:]['stage'])

    # ที่ต้องให้ id 6000 เพราะกลัวจะไปซ้ำกับของเดิม
    # latest_matches = pd.DataFrame(latest_match_data, columns=["match_id", "season", "stage", "date", "home_team_goal", "away_team_goal", "home_team", "away_team"])
    # เอา lastest_match_data ไปสร้างเป็น DF เก็บที่ชื่อ lastest_matches โดยกำหนด columns name ตามนั้น
    # latest_matches.head(20)
    # Add to full training data to predict current season
    matches = pd.concat([matches, matches_data_16, matches_data_17]) # เอาหลายๆ DF มารวมกัน แล้วเก็บไว้ที่ matches
    matches = matches.reset_index(drop=True)
    convert_team_name(matches)
    # Create a full set of match data that can be used with feature engineering later
    full_matches = matches.copy() # copy ไปไว้ที่ full_matches อีกอัน
    # print("-" * 50)
    # print(full_matches.tail(10))
    # print(full_matches.info())

    # --In[5]--
    # Set up the matches data how I need it
    # Add binary feature for W/D/L home and away
    determine_result(full_matches) # เรียกใช้ func เพื่อหาผล W/D/L มา และสร้าง column กำหนดมัน
    # Sort in date order
    full_matches.sort_values(by="date", inplace=True) # เรียงข้อมูล
    # print("*" * 50)
    # print(full_matches.head())

    # --In[6]--
    # Cope with newly promoted teams with limited or no stats
    # input ทีมที่เลื่อนชั้นมาเองของ แต่ละฤดูกาล เลยมีอย่างละ 3 รอบ
    # Value of dict ถ้าต้องการมีหลายๆค่า ควรใช้เป็น list
    team_data = {"team": [
        'West Bromwich Albion', 'Stoke City', 'Hull City',
        'Wolverhampton Wanderers', 'Birmingham City', 'Burnley',
        'Newcastle United', 'West Bromwich Albion', 'Blackpool',
        'Queens Park Rangers', 'Norwich City', 'Swansea City',
        'Reading', 'Southampton', 'West Ham United',
        'Cardiff City', 'Crystal Palace', 'Hull City',
        'Leicester City', 'Burnley', 'Queens Park Rangers',
        'Bournemouth', 'Watford', 'Norwich City',
        'Burnley', 'Middlesbrough', 'Hull City',
        'Brighton', 'Newcastle United', 'Huddersfield'
    ],
    "season":[
        "2008/2009", "2008/2009", "2008/2009",
        "2009/2010", "2009/2010", "2009/2010",
        "2010/2011", "2010/2011", "2010/2011",
        "2011/2012", "2011/2012", "2011/2012",
        "2012/2013", "2012/2013", "2012/2013",
        "2013/2014", "2013/2014", "2013/2014",
        "2014/2015", "2014/2015", "2014/2015",
        "2015/2016", "2015/2016", "2015/2016",
        "2016/2017", "2016/2017", "2016/2017",
        "2017/2018", "2017/2018", "2017/2018"
    ]}
    new_teams = pd.DataFrame(team_data, columns=["team", "season"]) # สร้างเป็น DF เก็บไว้
    # print("*" * 50)
    # print(new_teams.head())

    # --In[7]--
    # Cater for new teams by setting the new team for that season to a generic name
    for index, row in new_teams.iterrows(): # วนลูปแต่ละแถวของ new_teams โดย get index กับชื่อทีมพร้อมฤดูกาล
        for index1, row1 in full_matches.iterrows(): # วนลูปของ full_matches
            if (row1["home_team"] == row["team"]) & (row1["season"] == row["season"]):
                full_matches.loc[index1, "home_team"] = "Promoted"
            if (row1["away_team"] == row["team"]) & (row1["season"] == row["season"]):
                full_matches.loc[index1, "away_team"] = "Promoted"
            # ถ้าเป็นทีมที่เลื่อนชั้นขึ้นมาของฤดูกาลนั้น ให้เปลี่ยนชื่อทีมเป็น Promoted
    # print("*" * 50)
    # print(full_matches.head(20))

    # --In[8]--
    # Convert home & team into a binary feature, ie Arsenal_h or Arsenal_a
    # Need all seasons data for team binary feature
    # เอาทีมเหย้าและทีมเยือนมาใส่ h แล้วดึงสกอรืมาด้วย
    full_match_features = pd.DataFrame(full_matches[['season', 'stage']],
                                       columns=[['season', 'stage']]) # เอา column ของ full_matches มาสร้างเป็น DF ใหม่
    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['home_team']).rename(columns=lambda x: str(x) + '_h')],
        axis=1)
    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['away_team']).rename(columns=lambda x: str(x) + '_a')],
        axis=1)
    # print("*" * 50)
    # print(full_match_features.head())

    # --In[9]--
    # สร้าง DF ของ train
    # To predict this season (1, this week only, remove this week from training set
    train_match_features = full_match_features.loc[(full_match_features['season'] != this_season) |
                                                   (full_match_features['season'] == this_season) &
                                                   (full_match_features['stage'] < this_week)].copy() # copy ข้อมูลยกเว้นอาทิตย์นี้ไป
    train_match_features.drop(['season'], axis=1, inplace=True) # ลบ column season ออกไป เก็บไว้ในอันเดิม
    # print("*" * 50)
    # print(train_match_features.tail())

    # --In[10]--
    # Add the home team result column to the matches dataframe
    full_matches['home_team_result'] = full_matches.apply(determine_home_result, axis=1) # เรียก func determine..
    # สร้าง column ผลของทีมเหย้าไป
    # axis 1 -> น่าจะวนทีละหนึ่งแถว
    # To predict this season, this week, remove latest week from training results
    train_matches = full_matches.loc[(full_matches['season'] != this_season) |
                                     (full_matches['season'] == this_season) &
                                     (full_matches['stage'] < this_week)].copy() # copy DF ยกเว้นของอาทิตย์นี้
    targets = train_matches['home_team_result'].values # array ของ home team result
    # print("*" * 50)
    # print(train_matches.tail())

    # --In[11]--
    # Get the test matches in correct format:
    # Predict this season this week
    # สร้าง DF ของ test
    test_match_features = full_match_features.loc[(full_match_features['season'] == this_season) &
                                                  (full_match_features['stage'] == this_week)].copy()
    test_match_features.drop(['season'], axis=1, inplace=True) # remove season column
    # print("*" * 50)
    # print(test_match_features)

    # --In[12]--
    # Don't have the target results yet but I have entered dummy data of 0-0 draws.
    # Then re-run with actual scores after they are played for comparison
    # สร้าง df ของ อาทิตย์นี้ขึ้นมาโดย copy มาจากของทั้งหมด
    model_test_matches = full_matches.loc[(full_matches['season'] == this_season) &
                                          (full_matches['stage'] == this_week)].copy()
    model_test_matches = model_test_matches.reset_index(drop=True)
    # print("*" * 50)
    # print(model_test_matches)

    # --In[14]--
    # Train, then predict
    model = MultinomialNB()
    model.fit(train_match_features.values, targets)
    print('Accuracy of prediction = {}'.format(model.score(train_match_features.values, targets)))
    predicted = model.predict_proba(test_match_features.values)
    # Format the output into a DF with columns
    predicted_table = pd.DataFrame(predicted, columns=['draw', 'lose', 'win'])
    # Compare predicted with test actual results
    predicted_table['predict_res'] = predicted_table.apply(predict_home_result, axis=1)
    predicted_table['actual_res'] = model_test_matches['home_team_result']
    # Straight comparison - count of equal / total to get %
    # print("*" * 50)
    # print((predicted_table[predicted_table['predict_res']
    #                        == model_test_matches['home_team_result']].count()) / model_test_matches[
    #           'home_team_result'].count())

    # --In[15]--
    compare_results = model_test_matches[['match_id', 'stage', 'home_team_goal',
                                          'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results = pd.concat([compare_results, predicted_table], axis=1)
    # print("*" * 50)
    print(compare_results)