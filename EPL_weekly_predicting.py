# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import sqlalchemy
from sqlalchemy import create_engine # database connection
import sqlite3
import matplotlib.pyplot as plt

from IPython.display import display, clear_output
from sklearn.naive_bayes import MultinomialNB
from datetime import datetime
from sklearn.metrics import accuracy_score
import os

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
# print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.

import sys

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
# print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.

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

# State the result as home or away win/draw/lose - 6 possibilites
# Create a binary result
def determine_result(match_list):
    match_list['home_win'] = np.where(match_list['home_team_goal'] > match_list['away_team_goal'], 1, 0)
    match_list['home_draw'] = np.where(match_list['home_team_goal'] == match_list['away_team_goal'], 1, 0)
    match_list['home_lose'] = np.where(match_list['home_team_goal'] < match_list['away_team_goal'], 1, 0)
    match_list['away_win'] = np.where(match_list['home_team_goal'] < match_list['away_team_goal'], 1, 0)
    match_list['away_draw'] = np.where(match_list['home_team_goal'] == match_list['away_team_goal'], 1, 0)
    match_list['away_lose'] = np.where(match_list['home_team_goal'] > match_list['away_team_goal'], 1, 0)

# Get the target results for training

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
        matches_new = pd.read_sql('select * from match;', con)
        matches_schedule = pd.read_sql('select * from match_schedule;', con)
        team_rating = pd.read_sql('select * from team_rating;', con)

    # Parameters to change depending on season and wek we are running for
    last_season = matches_new.iat[-1, 1]
    last_stage = matches_new.iat[-1, 2]
    if last_stage == 38:
        first_season = int(last_season[:4]) + 1
        end_season = int(last_season[5:]) + 1
        this_season = f'{first_season}/{last_season}'
        this_week = (len(matches_new.loc[(matches_new['season'] == this_season)]) // 10) + 1
    else:
        this_season = last_season
        this_week = last_stage + 1
    train_ratio = .8
    model_weight = .8
    this_week

    matches_schedule = matches_schedule.loc[(matches_schedule['stage'] == this_week) & (matches_schedule['season'] == this_season)]
    # matches_schedule['match_id'] = match_id
    matches_schedule

    # Add to full training data to predict current season
    matches = pd.concat([matches, matches_new, matches_schedule])
    matches = matches.reset_index(drop=True)
    matches.drop(columns=['match_id', 'team_fifa_api_id_x', 'team_fifa_api_id_y'], inplace=True, axis=1)
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

    full_matches

    # Set up the matches data how I need it

    # Add binary feature for W/D/L home and away
    determine_result(full_matches)

    # Sort in date order
    # full_matches.sort_values(by='date', inplace=True)

    full_matches

    full_match_features = pd.DataFrame(full_matches[['season', 'stage']])
    # ,
    # columns=[['season', 'stage']])
    full_match_features

    team_rating.drop('team_rating_id', axis=1, inplace=True)
    team_rating2 = team_rating.copy()
    team_rating = team_rating.rename(columns={'team_name': 'home_team'})
    team_rating2 = team_rating2.rename(columns={'team_name': 'away_team'})

    full_matches = pd.merge(full_matches, team_rating, how='left', on=['season', 'home_team'])
    full_matches = full_matches.rename(columns={'attack_rating': 'home_team_attack_rating'})
    full_matches = full_matches.rename(columns={'midfield_rating': 'home_team_midfield_rating'})
    full_matches = full_matches.rename(columns={'defence_rating': 'home_team_defence_rating'})
    full_matches = full_matches.rename(columns={'team_rating': 'home_team_rating'})
    full_matches = pd.merge(full_matches, team_rating2, how='left', on=['season', 'away_team'])
    full_matches = full_matches.rename(columns={'attack_rating': 'away_team_attack_rating'})
    full_matches = full_matches.rename(columns={'midfield_rating': 'away_team_midfield_rating'})
    full_matches = full_matches.rename(columns={'defence_rating': 'away_team_defence_rating'})
    full_matches = full_matches.rename(columns={'team_rating': 'away_team_rating'})
    full_matches

    # Convert home & team into a binary feature, ie Arsenal_h or Arsenal_a
    # Need all seasons data for team binary feature
    full_match_features = pd.DataFrame(full_matches[['season', 'stage']])  # เอา column ไหนมาบ้าง
    #                                    columns=[['season', 'stage']])

    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['home_team']).rename(columns=lambda x: str(x) + '_h')],
        axis=1)
    full_match_features = pd.concat(
        [full_match_features, pd.get_dummies(full_matches['away_team']).rename(columns=lambda x: str(x) + '_a')],
        axis=1)

    full_match_features.head()  # ข้อมูลสถิติเก่าๆ

    # DataFrame team rating
    full_match_features_2 = pd.DataFrame(full_matches[['season', 'stage', 'home_team_attack_rating',
                                                       'home_team_midfield_rating', 'home_team_defence_rating',
                                                       'home_team_rating', 'away_team_attack_rating',
                                                       'away_team_midfield_rating', 'away_team_defence_rating',
                                                       'away_team_rating']])

    full_match_features_2.head()  # ข้อมูล team rating

    # To predict this season (1, this week only, remove this week from training set
    train_match_features = full_match_features.loc[:int(full_match_features.shape[0] * train_ratio)].copy()

    train_match_features.drop(['season'], axis=1, inplace=True)
    train_match_features.tail()

    # To predict this season (1, this week only, remove this week from training set
    train_match_features_2 = full_match_features_2.loc[:int(full_match_features.shape[0] * train_ratio)].copy()

    train_match_features_2.drop(['season', 'stage'], axis=1, inplace=True)
    train_match_features_2.tail()

    #   Add the home team result column to the matches dataframe
    full_matches['home_team_result'] = full_matches.apply(determine_home_result, axis=1)

    # To predict this season, this week, remove latest week from training results
    train_matches = full_matches.loc[:int(full_matches.shape[0] * train_ratio)].copy()

    targets = train_matches['home_team_result'].values
    train_matches.tail()

    # Get the test matches in correct format:

    # Predict this season this week
    test_match_features = full_match_features.loc[int(full_match_features.shape[0] * train_ratio):].copy()

    test_match_features.drop(full_match_features.index[-10:], inplace=True)
    test_match_features.drop(['season'], axis=1, inplace=True)
    test_match_features

    test_match_features_1 = full_match_features.iloc[-10:].copy()
    test_match_features_1.drop(['season'], axis=1, inplace=True)
    test_match_features_1

    test_match_features_2 = full_match_features_2.loc[int(full_match_features.shape[0] * train_ratio):].copy()

    test_match_features_2.drop(full_match_features.index[-10:], inplace=True)
    test_match_features_2.drop(['season', 'stage'], axis=1, inplace=True)
    test_match_features_2

    test_match_features_2_1 = full_match_features_2.iloc[-10:].copy()
    test_match_features_2_1.drop(['season', 'stage'], axis=1, inplace=True)
    test_match_features_2_1

    # Don't have the target results yet but I have entered dummy data of 0-0 draws.
    # Then re-run with actual scores after they are played for comparison
    model_test_matches = full_matches.loc[int(full_matches.shape[0] * train_ratio):].copy()
    # model_test_matches = full_matches.loc[(full_matches['season'] == this_season) &
    #                                      (full_matches['stage'] == this_week - 1)].copy()

    model_test_matches.drop(full_match_features.index[-10:], inplace=True)
    model_test_matches = model_test_matches.reset_index(drop=True)
    model_test_matches

    model_test_matches_1 = full_matches.iloc[-10:].copy()
    # model_test_matches = full_matches.loc[(full_matches['season'] == this_season) &
    #                                      (full_matches['stage'] == this_week - 1)].copy()

    # model_test_matches.drop(full_match_features.index[-10:], inplace=True)
    model_test_matches_1 = model_test_matches_1.reset_index(drop=True)
    model_test_matches_1

    # Train, then predict
    model = MultinomialNB()

    model.fit(train_match_features.values, targets)  # รับเป็น array ของสิ่งที่จะทำนายและผลเข้าไป
    predicted = model.predict_proba(test_match_features.values)  # รับเป็น array อาทิตที่จะทำนายต่อไป

    # Format the output into a DF with columns
    predicted_table = pd.DataFrame(predicted, columns=['draw', 'lose', 'win'])

    # Compare predicted with test actual results
    predicted_table['predict_res'] = predicted_table.apply(predict_home_result, axis=1)
    predicted_table['actual_res'] = model_test_matches['home_team_result']

    # Straight comparison - count of equal / total to get %
    (predicted_table[predicted_table['predict_res']
                     == model_test_matches['home_team_result']].count()) / model_test_matches[
        'home_team_result'].count()

    predicted_1 = model.predict_proba(test_match_features_1.values)  # รับเป็น array อาทิตที่จะทำนายต่อไป

    # Format the output into a DF with columns
    predicted_table_1 = pd.DataFrame(predicted_1, columns=['draw', 'lose', 'win'])

    # Compare predicted with test actual results
    predicted_table_1['predict_res'] = predicted_table_1.apply(predict_home_result, axis=1)
    predicted_table_1['actual_res'] = model_test_matches_1['home_team_result']

    # Straight comparison - count of equal / total to get %
    (predicted_table_1[predicted_table_1['predict_res']
                       == model_test_matches_1['home_team_result']].count()) / model_test_matches_1[
        'home_team_result'].count()

    # Train, then predict
    model_2 = MultinomialNB()

    model_2.fit(train_match_features_2.values, targets)  # รับเป็น array ของสิ่งที่จะทำนายและผลเข้าไป
    predicted_2 = model_2.predict_proba(test_match_features_2.values)  # รับเป็น array อาทิตที่จะทำนายต่อไป

    # Format the output into a DF with columns
    predicted_table_2 = pd.DataFrame(predicted_2, columns=['draw', 'lose', 'win'])

    # Compare predicted with test actual results
    predicted_table_2['predict_res'] = predicted_table_2.apply(predict_home_result, axis=1)
    predicted_table_2['actual_res'] = model_test_matches['home_team_result']

    # Straight comparison - count of equal / total to get %
    (predicted_table_2[predicted_table_2['predict_res']
                       == model_test_matches['home_team_result']].count()) / model_test_matches[
        'home_team_result'].count()

    predicted_2_1 = model_2.predict_proba(test_match_features_2_1.values)  # รับเป็น array อาทิตที่จะทำนายต่อไป

    # Format the output into a DF with columns
    predicted_table_2_1 = pd.DataFrame(predicted_2_1, columns=['draw', 'lose', 'win'])

    # Compare predicted with test actual results
    predicted_table_2_1['predict_res'] = predicted_table_2_1.apply(predict_home_result, axis=1)
    predicted_table_2_1['actual_res'] = model_test_matches_1['home_team_result']

    # Straight comparison - count of equal / total to get %
    (predicted_table_2_1[predicted_table_2_1['predict_res']
                         == model_test_matches_1['home_team_result']].count()) / model_test_matches_1[
        'home_team_result'].count()

    compare_results = model_test_matches[['stage', 'home_team_goal',
                                          'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results = pd.concat([compare_results, predicted_table], axis=1)
    compare_results = compare_results[
        ['stage', 'h_goal', 'a_goal', 'home_team', 'predict_res', 'away_team', 'draw', 'lose', 'win', 'actual_res']]
    compare_results = compare_results.rename(columns={'predict_res': 'predict_result'})
    compare_results.tail(10)

    compare_results_2 = model_test_matches[['stage', 'home_team_goal',
                                            'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results_2.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results_2 = pd.concat([compare_results_2, predicted_table_2], axis=1)
    compare_results_2 = compare_results_2[
        ['stage', 'h_goal', 'a_goal', 'home_team', 'predict_res', 'away_team', 'draw', 'lose', 'win', 'actual_res']]
    compare_results_2 = compare_results_2.rename(columns={'predict_res': 'predict_result'})
    compare_results_2.tail(10)

    compare_results_3 = compare_results.copy()

    # weight data
    compare_results_3['draw'] = compare_results['draw'] * model_weight + compare_results_2['draw'] * (1 - model_weight)
    compare_results_3['lose'] = compare_results['lose'] * model_weight + compare_results_2['lose'] * (1 - model_weight)
    compare_results_3['win'] = compare_results['win'] * model_weight + compare_results_2['win'] * (1 - model_weight)
    compare_results_3['predict_result'] = compare_results_3.apply(predict_home_result, axis=1)
    compare_results_3.tail(10)

    # evaluate accuracy of train data
    print(
        'Accuracy of train data (old match) = {:.2f}%'.format(model.score(train_match_features.values, targets) * 100))

    print('Accuracy of train data (team rating) = {:.2f}%'.format(
        model_2.score(train_match_features_2.values, targets) * 100))

    # evaluate accuracy of prediction
    print('Accuracy of prediction (old match) = {:.2f}%'.format(
        accuracy_score(compare_results['actual_res'], compare_results['predict_result']) * 100))

    print('Accuracy of prediction (team rating) = {:.2f}%'.format(
        accuracy_score(compare_results_2['actual_res'], compare_results_2['predict_result']) * 100))

    # targets # ผลการแข่งขันจริงๆ
    print('Total accuracy of prediction = {:.2f}%'.format(
        accuracy_score(compare_results_3['actual_res'], compare_results_3['predict_result']) * 100))

    compare_results_1_1 = model_test_matches_1[['stage', 'home_team_goal',
                                                'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results_1_1.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results_1_1 = pd.concat([compare_results_1_1, predicted_table_1], axis=1)
    compare_results_1_1 = compare_results_1_1[
        ['stage', 'h_goal', 'a_goal', 'home_team', 'predict_res', 'away_team', 'draw', 'lose', 'win', 'actual_res']]
    compare_results_1_1 = compare_results_1_1.rename(columns={'predict_res': 'predict_result'})
    compare_results_1_1

    compare_results_2_1 = model_test_matches_1[['stage', 'home_team_goal',
                                                'away_team_goal', 'home_team', 'away_team']].copy()
    compare_results_2_1.rename(columns={'home_team_goal': 'h_goal', 'away_team_goal': 'a_goal'}, inplace=True)
    compare_results_2_1 = pd.concat([compare_results_2_1, predicted_table_2_1], axis=1)
    compare_results_2_1 = compare_results_2_1[
        ['stage', 'h_goal', 'a_goal', 'home_team', 'predict_res', 'away_team', 'draw', 'lose', 'win', 'actual_res']]
    compare_results_2_1 = compare_results_2_1.rename(columns={'predict_res': 'predict_result'})
    compare_results_2_1

    compare_results_3_1 = compare_results_1_1.copy()

    # weight data
    compare_results_3_1['draw'] = compare_results_1_1['draw'] * model_weight + compare_results_2_1['draw'] * (
                1 - model_weight)
    compare_results_3_1['lose'] = compare_results_1_1['lose'] * model_weight + compare_results_2_1['lose'] * (
                1 - model_weight)
    compare_results_3_1['win'] = compare_results_1_1['win'] * model_weight + compare_results_2_1['win'] * (
                1 - model_weight)
    compare_results_3_1['predict_result'] = compare_results_3_1.apply(predict_home_result, axis=1)
    compare_results_3_1.drop('actual_res', axis=1, inplace=True)
    compare_results_3_1

    print(compare_results_3_1) # เชื่อม php แล้วไม่ต้องการให้ output ตัวนี้ออกไป

    # remove json file
    try:
        os.remove('result.JSON')
    except OSError:
        pass

    # save result table to json file
    # result_json = compare_results.to_json(orient='records')
    result_json = compare_results_3_1.to_json("result.JSON", orient='records')
    # print(result_json)

