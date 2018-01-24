# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy import create_engine # database connection
import sqlite3

from IPython.display import display, clear_output
from sklearn.naive_bayes import MultinomialNB
from datetime import datetime

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
# print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.

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
            if date_dif.days < 13:
                dict2[i] = dict2[i - 1] + 7
            if date_dif.days >= 13:
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
        if row['home_team'] == 'Brighton & Hove Albion':
            last_season.loc[index, 'home_team'] = 'Brighton'
        if row['home_team'] == 'Huddersfield Town':
            last_season.loc[index, 'home_team'] = 'Huddersfield'

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
        if row['away_team'] == 'Brighton & Hove Albion':
            last_season.loc[index, 'away_team'] = 'Brighton'
        if row['away_team'] == 'Huddersfield Town':
            last_season.loc[index, 'away_team'] = 'Huddersfield'
    return last_season

def create_match_id():
    match_id_num = []
    match_id_num2 = []
    for i in range(1, 11):
        match_id_num.append(i)
    for i in match_id_num:
        match_id_num2.append(i + int(last_season[-1:]['match_id']))
    return match_id_num2

def determine_result(match_list):
    match_list['home_win'] = np.where(match_list['home_team_goal'] > match_list['away_team_goal'], 1, 0)
    match_list['home_draw'] = np.where(match_list['home_team_goal'] == match_list['away_team_goal'], 1, 0)
    match_list['home_lose'] = np.where(match_list['home_team_goal'] < match_list['away_team_goal'], 1, 0)
    match_list['away_win'] = np.where(match_list['home_team_goal'] < match_list['away_team_goal'], 1, 0)
    match_list['away_draw'] = np.where(match_list['home_team_goal'] == match_list['away_team_goal'], 1, 0)
    match_list['away_lose'] = np.where(match_list['home_team_goal'] > match_list['away_team_goal'], 1, 0)

# Function to determine whether result is a win/draw/lose
def determine_home_result(match):
    if match['home_team_goal'] > match['away_team_goal']:
        return 'win'
    elif match['home_team_goal'] < match['away_team_goal']:
        return 'lose'
    else:
        return 'draw'

# Function to determine whether the highest prediction is for win/draw/lose

def predict_home_result(match):
    if (match['win'] >= match['draw']) & (match['win'] >= match['lose']):
        return 'win' # Favour a home win if probability equal
    elif (match['lose'] > match['win']) & (match['lose'] > match['draw']):
        return 'lose'
    else:
        return 'draw'

def result_plot(inp): # plot result
    if compare_results[compare_results['home_team'].str.contains(inp)].empty == False:
        list_res = [compare_results.loc[compare_results['home_team'].str.contains(inp), 'win'].to_string(index=False),
                    compare_results.loc[compare_results['home_team'].str.contains(inp), 'draw'].to_string(index=False),
                    compare_results.loc[compare_results['home_team'].str.contains(inp), 'lose'].to_string(index=False)]
        label = np.array(['Win', 'Draw', 'Lose'])
        color = ['green', 'yellow', 'red']
        print(list_res)
        plt.pie(list_res, labels=label, startangle=90, colors=color, autopct='%1.2f%%')
        plt.show()
    elif compare_results[compare_results['away_team'].str.contains(inp)].empty == False:
        list_res = [compare_results.loc[compare_results['away_team'].str.contains(inp), 'win'].to_string(index=False),
                    compare_results.loc[compare_results['away_team'].str.contains(inp), 'draw'].to_string(index=False),
                    compare_results.loc[compare_results['away_team'].str.contains(inp), 'lose'].to_string(index=False)]
        label = np.array(['Lose', 'Draw', 'Win'])
        color = ['red', 'yellow', 'green']
        print(list_res)
        plt.pie(list_res, labels=label, startangle=90, colors=color, autopct='%1.2f%%')
        plt.show()

def Next_week_result():
    week_array = np.array([])
    for _ in range(10):
        this_week_result = input('How does home team result ([W]in, [D]raw, [L]ose]) : ')
        if this_week_result.capitalize() == 'W':
            week_array = np.append(week_array, ['win'])
        elif this_week_result.capitalize() == 'D':
            week_array = np.append(week_array, ['draw'])
        elif this_week_result.capitalize() == 'L':
            week_array = np.append(week_array, ['lose'])
        else:
            print('Error result')
    return week_array

if __name__ == '__main__':
    # engine  = create_engine("sqlite:///../input/database.sqlite")
    with sqlite3.connect('database.sqlite') as engine:
        #    matches = pd.read_sql_query('SELECT * FROM Match where league_id = 1729 and season in ("2010/2011", "2011/2012", "2012/2013", "2013/2014", "2014/2015", "2015/2016");'
        #                                          , engine)
        matches = pd.read_sql_query('SELECT * FROM Match where league_id = 1729 ;', engine)

    matches = matches[matches.columns[:11]]
    teams = pd.read_sql_query('SELECT * FROM Team;', engine)

    # Add team names & tidy up
    matches = pd.merge(left=matches, right=teams, how='left', left_on='home_team_api_id', right_on='team_api_id')
    matches = matches.drop(['country_id', 'league_id', 'home_team_api_id', 'id_y', 'team_api_id', 'team_short_name'],
                           axis=1)
    matches.rename(columns={'id_x': 'match_id', 'team_long_name': 'home_team'}, inplace=True)
    matches = pd.merge(left=matches, right=teams, how='left', left_on='away_team_api_id', right_on='team_api_id')
    matches = matches.drop(['id', 'match_api_id', 'away_team_api_id', 'team_api_id', 'team_short_name'], axis=1)
    matches.rename(columns={'id_x': 'match_id', 'team_long_name': 'away_team'}, inplace=True)

    matches.tail(20)
    # matches.info()

    with sqlite3.connect('database2.sqlite') as con:
        matches_data_16 = pd.read_sql('select * from match;', con)
        matches_data_17 = pd.read_sql('select * from match17;', con)
        matches_schedule = pd.read_sql('select * from match_schedule3;', con)
    # matches_data_16['date'] = pd.to_datetime(matches_data_16['date'])

    matches_data_16 = convert_date_to_code16(matches_data_16)
    matches_data_17 = convert_date_to_code17(matches_data_17)
    matches_schedule = convert_date_to_code17(matches_schedule)
    last_season = pd.concat([matches_data_16, matches_data_17])
    # last_season.tail()
    # int(last_season[-1:]['match_id'])
    # matches_schedule.set_index('index', inplace=True)
    # matches_schedule.columns = ['date', 'home_team_goal', 'away_team_goal', 'home_team', 'away_team', 'season', 'stage']
    # matches_schedule = convert_team_name(matches_schedule)
    # matches_schedule.head(190)
    match_id = create_match_id()
    # match_id

    # Parameters to change depending on season and wek we are running for
    this_season = '2017/2018'
    this_week = int(matches_data_17[-1:]['stage']) + 1
    this_week

    matches_schedule = matches_schedule.loc[matches_schedule['stage'] == this_week]
    matches_schedule['match_id'] = match_id
    matches_schedule

    # Add to full training data to predict current season
    matches = pd.concat([matches, last_season, matches_schedule])
    matches = matches.reset_index(drop=True)
    convert_team_name(matches)
    # matches

    # Create a full set of match data that can be used with feature engineering later
    full_matches = matches.copy()
    # full_matches.match_id.fillna(last_season['match_id'][-1:] + 1)
    full_matches

    full_matches.drop(matches[matches.season == '2008/2009'].index, inplace=True)
    full_matches.drop(matches[matches.season == '2009/2010'].index, inplace=True)
    full_matches.drop(matches[matches.season == '2010/2011'].index, inplace=True)
    full_matches.drop(matches[matches.season == '2011/2012'].index, inplace=True)
    # Only use the seasons we require - Optimum appears to be for season 12/13 onwards

    # unique_seasons = pd.Series(matches['season'].unique())
    # exclude_seasons = pd.Series(['2008/2009', '2009/2010', '2010/2011', '2011/2012'])
    # include_seasons = unique_seasons[~unique_seasons.isin(exclude_seasons)]
    # full_matches = full_matches.loc[full_matches['season'].isin(include_seasons)]
    # full_matches.reset_index(drop=True, inplace=True)
    full_matches

    # Set up the matches data how I need it

    # Add binary feature for W/D/L home and away
    determine_result(full_matches)

    # Sort in date order
    full_matches.sort_values(by='date', inplace=True)

    full_matches.head()

    # Cope with newly promoted teams with limited or no stats
    team_data = {'team': ['West Bromwich Albion', 'Stoke City', 'Hull City',
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
                 'season': ["2008/2009", "2008/2009", "2008/2009",
                            "2009/2010", "2009/2010", "2009/2010",
                            "2010/2011", "2010/2011", "2010/2011",
                            "2011/2012", "2011/2012", "2011/2012",
                            "2012/2013", "2012/2013", "2012/2013",
                            "2013/2014", "2013/2014", "2013/2014",
                            "2014/2015", "2014/2015", "2014/2015",
                            "2015/2016", "2015/2016", "2015/2016",
                            "2016/2017", "2016/2017", "2016/2017",
                            "2017/2018", "2017/2018", "2017/2018"
                            ]
                 }
    new_teams = pd.DataFrame(team_data, columns=['team', 'season'])
    new_teams.head()

    # Cater for new teams by setting the new team for that season to a generic name

    for index, row in new_teams.iterrows():
        for index1, row1 in full_matches.iterrows():
            if (row1['home_team'] == row['team']) & (row1['season'] == row['season']):
                full_matches.loc[index1, 'home_team'] = 'Promoted'
            if (row1['away_team'] == row['team']) & (row1['season'] == row['season']):
                full_matches.loc[index1, 'away_team'] = 'Promoted'

    full_matches.head(20)

    full_match_features = pd.DataFrame(full_matches[['season', 'stage']])
    # ,
    # columns=[['season', 'stage']])
    full_match_features.head()

    # Convert home & team into a binary feature, ie Arsenal_h or Arsenal_a
    # Need all seasons data for team binary feature
    full_match_features = pd.DataFrame(full_matches[['season', 'stage']])
    #                                    columns=[['season', 'stage']])

    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['home_team']).rename(columns=lambda x: str(x) + '_h')],
        axis=1)
    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['away_team']).rename(columns=lambda x: str(x) + '_a')],
        axis=1)

    full_match_features.head()

    # To predict this season (1, this week only, remove this week from training set
    train_match_features = full_match_features.loc[(full_match_features['season'] != this_season) |
                                                   (full_match_features['season'] == this_season) &
                                                   (full_match_features['stage'] < this_week)].copy()

    train_match_features.drop(['season'], axis=1, inplace=True)
    train_match_features.tail()

    #   Add the home team result column to the matches dataframe
    full_matches['home_team_result'] = full_matches.apply(determine_home_result, axis=1)

    # To predict this season, this week, remove latest week from training results
    train_matches = full_matches.loc[(full_matches['season'] != this_season) |
                                     (full_matches['season'] == this_season) &
                                     (full_matches['stage'] < this_week)].copy()

    targets = train_matches['home_team_result'].values
    train_matches.tail()

    # Get the test matches in correct format:

    # Predict this season this week
    test_match_features = full_match_features.loc[(full_match_features['season'] == this_season) &
                                                  (full_match_features['stage'] == this_week)].copy()

    test_match_features.drop(['season'], axis=1, inplace=True)
    test_match_features

    # Don't have the target results yet but I have entered dummy data of 0-0 draws.
    # Then re-run with actual scores after they are played for comparison
    model_test_matches = full_matches.loc[(full_matches['season'] == this_season) &
                                          (full_matches['stage'] == this_week)].copy()
    # model_test_matches = full_matches.loc[(full_matches['season'] == this_season) &
    #                                      (full_matches['stage'] == this_week - 1)].copy()

    model_test_matches = model_test_matches.reset_index(drop=True)
    model_test_matches

    # ดึงผลโหวตของการแข่งขันนัดต่อไปมาช่วยในการทำนาย
    train_match_features = pd.concat([train_match_features, test_match_features]) # ต้องใช้ข้อมูลการแข่งนัดต่อไปด้วย
    target_this_week = Next_week_result() # รับผลโหวตเป็น array
    targets = np.append(targets, target_this_week) # เอาตัวหลังไปต่อตัวหน้า

    # Train, then predict
    model = MultinomialNB()
    # np.place(targets, targets == 'draw', ['lose'])
    # targets
    model.fit(train_match_features.values, targets) # train model
    predicted = model.predict_proba(test_match_features.values) # predicted จะมีกี่แบบ ขึ้นอยู่ target ที่เราเคย train มาว่าแบ่งได้เป็นกี่คำตอบ

    # Format the output into a DF with columns
    predicted_table = pd.DataFrame(predicted, columns=['draw', 'lose', 'win'])

    # Compare predicted with test actual results
    predicted_table['predict_res'] = predicted_table.apply(predict_home_result, axis=1)
    predicted_table['actual_res'] = model_test_matches['home_team_result']

    # Straight comparison - count of equal / total to get %
    (predicted_table[predicted_table['predict_res']
                     == model_test_matches['home_team_result']].count()) / model_test_matches[
        'home_team_result'].count()

    # evaluate accuracy of prediction
    print('Accuracy of prediction = {:.2f}%'.format(model.score(train_match_features.values, targets) * 100))

    compare_results = model_test_matches[['match_id', 'stage', 'home_team_goal',
                                          'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results = pd.concat([compare_results, predicted_table], axis=1)
    print(compare_results)

    # get favorite team to show result graph
    inp = input('Team name : ')
    result_plot(inp)