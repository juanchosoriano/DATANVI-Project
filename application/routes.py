from application import app
from flask import render_template, url_for, request
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import FuncFormatter
import numpy as np 
import math
import seaborn as sns

url = 'https://raw.githubusercontent.com/angelinegubat/DATANVI-DATA/main/archive/GamingStudy_data.csv'
ga_df = pd.read_csv(url,encoding='latin1')  

GameAnxiety = ga_df[['S. No.', 'Gender', 'Age', 'Playstyle', 'Platform', 'whyplay', 'GAD1', 'GAD2', 'GAD3', 'GAD4', 'GAD5', 'GAD6', 'GAD7', 'SWL1', 'SWL2', 'SWL3', 'SWL4', 'SWL5', 'SPIN1', 'SPIN2', 'SPIN3', 'SPIN4', 'SPIN5', 'SPIN6', 'SPIN7', 'SPIN8', 'SPIN9', 'SPIN10', 'SPIN11', 'SPIN12', 'SPIN13', 'SPIN14', 'SPIN15', 'SPIN16', 'SPIN17', 'GAD_T', 'SWL_T', 'SPIN_T']]
GameAnxiety = GameAnxiety[GameAnxiety['SPIN_T'].notna()]

GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('all', case=False), 'whyplay'] = "All of the above"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('winning', case=False), 'whyplay'] = "winning"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('win', case=False), 'whyplay'] = "winning"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('fun', case=False), 'whyplay'] = "having fun"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('time', case=False), 'whyplay'] = "pass time"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('improving', case=False), 'whyplay'] = "improving"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('learning', case=False), 'whyplay'] = "improving"
GameAnxiety.loc[GameAnxiety['whyplay'].str.contains('friends', case=False), 'whyplay'] = "friends"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('all', case = False), 'Playstyle'] = "All of the above"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('online', case = False), 'Playstyle'] = "Multiplayer - Online"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('offline', case = False), 'Playstyle'] = "Multiplayer - Offline"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('strangers', case = False), 'Playstyle'] = "Multiplayer - Online"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('friends', case = False), 'Playstyle'] = "Multiplayer - Online"
GameAnxiety.loc[GameAnxiety['Playstyle'].str.contains('singleplayer' or 'Singleplayer', case = False), 'Playstyle'] = "Singleplayer"

GameAnxiety['SWL1'] = GameAnxiety['SWL1'] - 1
GameAnxiety['SWL2'] = GameAnxiety['SWL2'] - 1
GameAnxiety['SWL3'] = GameAnxiety['SWL3'] - 1
GameAnxiety['SWL4'] = GameAnxiety['SWL4'] - 1
GameAnxiety['SWL5'] = GameAnxiety['SWL5'] - 1
col_list = ['SWL1', 'SWL2', 'SWL3', 'SWL4', 'SWL5']
GameAnxiety['SWL_T'] = GameAnxiety[col_list].sum(axis=1)

GAD_TOTAL = 21
SWL_TOTAL = 30
SPIN_TOTAL = 68
TESTS_TOTAL = GAD_TOTAL + SWL_TOTAL + SPIN_TOTAL

Gamer_Age = GameAnxiety[['Age', 'GAD_T', 'SWL_T', 'SPIN_T']]
Game_Age_Copy = GameAnxiety[['Age', 'GAD_T', 'SWL_T', 'SPIN_T']]

n_age_group = 5
age_max = Gamer_Age['Age'].max()
age_min = Gamer_Age['Age'].min()

Gamer_Age['Age'] = pd.cut(Gamer_Age['Age'], n_age_group)
age_n_range = (age_max - age_min) / n_age_group
GA_grouped = Gamer_Age.groupby('Age').sum()
intervals = GA_grouped.index

i = age_min
age_ranges = []
while(i < age_max):
    ages = str(math.ceil(i)) + " to " + str(math.floor(i + age_n_range))
    age_ranges.append(ages)
    i += age_n_range

for i in range(len(age_ranges)):
    Gamer_Age['Age'] = np.where(Gamer_Age['Age'] == intervals[i], age_ranges[i], Gamer_Age['Age'])

GamerSplitG = Gamer_Age[['Age', 'GAD_T']]
GamerSplitG["Questionnaire Type"] = "GAD"
GamerSplitW = Gamer_Age[['Age', 'SWL_T']]
GamerSplitW["Questionnaire Type"] = "SWL"
GamerSplitP = Gamer_Age[['Age', 'SPIN_T']]
GamerSplitP["Questionnaire Type"] = "SPIN"

GamerFlatten = pd.DataFrame({'Age': GamerSplitG['Age'], 'Type': GamerSplitG['Questionnaire Type'], 'Score': GamerSplitG['GAD_T']})
GamerFlattenP = pd.DataFrame({'Age': GamerSplitP['Age'], 'Type': GamerSplitP['Questionnaire Type'], 'Score': GamerSplitP['SPIN_T']})
GamerFlattenW = pd.DataFrame({'Age': GamerSplitW['Age'], 'Type': GamerSplitW['Questionnaire Type'], 'Score': GamerSplitW['SWL_T']})
GamerFlatten = GamerFlatten.append(GamerFlattenP, ignore_index = True)
GamerFlatten = GamerFlatten.append(GamerFlattenW, ignore_index = True)
GamerFlatten = GamerFlatten.sort_values('Age')

playstyle = GameAnxiety[['Playstyle', 'GAD_T', 'SWL_T', 'SPIN_T']]
Gamer_Reason = GameAnxiety[['whyplay', 'GAD_T', 'SWL_T', 'SPIN_T']]

user_age = 19
@app.route('/')
def index():
    return render_template('index.html', title = "Home Page")

@app.route('/ageGroup')
def ageGroup():
    Age2_fig = px.strip(GamerFlatten, x='Score', y="Type", color='Age', color_discrete_map = {"18 to 25": "#6F5F90", "26 to 33": "#FF7B89", "34 to 40": "#8A5082", "41 to 48": "#758EB7", "49 to 56": "#A5CAD2" })
    graph1JSON = json.dumps(Age2_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Age Group.html', graph1JSON=graph1JSON)

@app.route('/Gender')
def Gender():
    GamerGender = GameAnxiety[['Gender', 'GAD_T', 'SWL_T', 'SPIN_T']]

    GamerSplitG2 = GamerGender[['Gender', 'GAD_T']]
    GamerSplitG2["Questionnaire Type"] = "GAD"
    GamerSplitW2 = GamerGender[['Gender', 'SWL_T']]
    GamerSplitW2["Questionnaire Type"] = "SWL"
    GamerSplitP2 = GamerGender[['Gender', 'SPIN_T']]
    GamerSplitP2["Questionnaire Type"] = "SPIN"

    GamerFlatten2 = pd.DataFrame({'Gender': GamerSplitG2['Gender'], 'Type': GamerSplitG2['Questionnaire Type'], 'Score': GamerSplitG2['GAD_T']})
    GamerFlattenP2 = pd.DataFrame({'Gender': GamerSplitP2['Gender'], 'Type': GamerSplitP2['Questionnaire Type'], 'Score': GamerSplitP2['SPIN_T']})
    GamerFlattenW2 = pd.DataFrame({'Gender': GamerSplitW2['Gender'], 'Type': GamerSplitW2['Questionnaire Type'], 'Score': GamerSplitW2['SWL_T']})
    GamerFlatten2 = GamerFlatten2.append(GamerFlattenP2, ignore_index = True)
    GamerFlatten2 = GamerFlatten2.append(GamerFlattenW2, ignore_index = True)
    GamerFlatten2 = GamerFlatten2.sort_values('Gender')

    Gender_fig = px.strip(GamerFlatten2, x='Score', y="Type", color='Gender', color_discrete_map = {"Male": "#96B9D0", "Female": "#EBA7AC", "Other": "#B399D4"})

    graph2JSON = json.dumps(Gender_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Gender.html', graph2JSON=graph2JSON)

@app.route('/Playstyle')
def Playstyle():
    

    playstyle.loc[(playstyle['Playstyle'] != "Singleplayer") & (playstyle['Playstyle'] != "Multiplayer - Online") &(playstyle['Playstyle'] != "Multiplayer - Offline") & (playstyle['Playstyle'] != "All of the above"), 'Playstyle'] = "Others"
    GamerSplitG4 = playstyle[['Playstyle', 'GAD_T']]
    GamerSplitG4["Questionnaire Type"] = "GAD"
    GamerSplitW4 = playstyle[['Playstyle', 'SWL_T']]
    GamerSplitW4["Questionnaire Type"] = "SWL"
    GamerSplitP4 = playstyle[['Playstyle', 'SPIN_T']]
    GamerSplitP4["Questionnaire Type"] = "SPIN"

    GamerFlatten4 = pd.DataFrame({'Playstyle': GamerSplitG4['Playstyle'], 'Type': GamerSplitG4['Questionnaire Type'], 'Score': GamerSplitG4['GAD_T']})
    GamerFlattenP4 = pd.DataFrame({'Playstyle': GamerSplitP4['Playstyle'], 'Type': GamerSplitP4['Questionnaire Type'], 'Score': GamerSplitP4['SPIN_T']})
    GamerFlattenW4 = pd.DataFrame({'Playstyle': GamerSplitW4['Playstyle'], 'Type': GamerSplitW4['Questionnaire Type'], 'Score': GamerSplitW4['SWL_T']})
    GamerFlatten4 = GamerFlatten4.append(GamerFlattenP4, ignore_index = True)
    GamerFlatten4 = GamerFlatten4.append(GamerFlattenW4, ignore_index = True)
    GamerFlatten4 = GamerFlatten4.sort_values('Playstyle', ascending=False)

    Playstyle_fig = px.strip(GamerFlatten4, x='Score', y="Type", color='Playstyle', color_discrete_map = {"Multiplayer - Offline": "#6F5F90",
                "Multiplayer - Online": "#FF7B89",
                "Singleplayer": "#8A5082",
                "All of the above": "#758EB7",
                "Others": "#A5CAD2"})
    graph3JSON = json.dumps(Playstyle_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('Playstyle.html', graph3JSON=graph3JSON)

@app.route('/Reason')
def Reason():
    
    Gamer_Reason.loc[(Gamer_Reason['whyplay'] != "having fun") & (Gamer_Reason['whyplay'] != "improving") &(Gamer_Reason['whyplay'] != "winning") & (Gamer_Reason['whyplay'] != "relaxing") & (Gamer_Reason['whyplay'] != "All of the above"), 'whyplay'] = "Others"
   
    GamerSplitG3 = Gamer_Reason[['whyplay', 'GAD_T']]
    GamerSplitG3["Questionnaire Type"] = "GAD"
    GamerSplitW3 = Gamer_Reason[['whyplay', 'SWL_T']]
    GamerSplitW3["Questionnaire Type"] = "SWL"
    GamerSplitP3 = Gamer_Reason[['whyplay', 'SPIN_T']]
    GamerSplitP3["Questionnaire Type"] = "SPIN"

    GamerFlatten3 = pd.DataFrame({'whyplay': GamerSplitG3['whyplay'], 'Type': GamerSplitG3['Questionnaire Type'], 'Score': GamerSplitG3['GAD_T']})
    GamerFlattenP3 = pd.DataFrame({'whyplay': GamerSplitP3['whyplay'], 'Type': GamerSplitP3['Questionnaire Type'], 'Score': GamerSplitP3['SPIN_T']})
    GamerFlattenW3 = pd.DataFrame({'whyplay': GamerSplitW3['whyplay'], 'Type': GamerSplitW3['Questionnaire Type'], 'Score': GamerSplitW3['SWL_T']})
    GamerFlatten3 = GamerFlatten3.append(GamerFlattenP3, ignore_index = True)
    GamerFlatten3 = GamerFlatten3.append(GamerFlattenW3, ignore_index = True)
    GamerFlatten3 = GamerFlatten3.sort_values('whyplay', ascending=False)

    Reason_fig = px.strip(GamerFlatten3, x='Score', y="Type", color='whyplay', color_discrete_map = {"having fun": "#FF7B89",
                "improving": "#8A5082",
                "winning": "#6F5F90",
                "relaxing": "#758EB7",
                "All of the above": "#A5CAD2",
                "Others": "#a0b0cf"})
    graph4JSON = json.dumps(Reason_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('Reason.html', graph4JSON=graph4JSON)

@app.route('/Final', methods = ['GET', 'POST'])
def Final():
    if request.method == 'GET':
        filter_age = 30
        filter_gender = "Male"
        filter_reason = "having fun"
        filter_playstyle = "Singleplayer"

        
        Filtering = GameAnxiety[['Age', 'Gender', 'GAD_T', 'SWL_T', 'SPIN_T']]
        Filtering['Playstyle'] = playstyle['Playstyle']
        Filtering['whyplay'] = Gamer_Reason['whyplay'] 
        choices_gender = ['Male', 'Female', 'Others']
        choices_playstyle = ['Singleplayer', 'Multiplayer - Offline', 'Multiplayer - Online', 'All of the above', 'Others']
        choices_reasons = ['having fun', 'improving', 'winning', 'relaxing', 'All of the above', 'Others']
        n_age_group = 5
        Filtering['Age'] = pd.cut(Filtering['Age'], n_age_group)
        
        for i in intervals:
            if filter_age in i:
                user_group = i
                break
        Filtered_df = Filtering[(Filtering['Age'] == user_group) & (Filtering['Gender'] == filter_gender) & (Filtering['whyplay'] == filter_reason) & (Filtering['Playstyle'] == filter_playstyle)]
        Filtered_group_df = Filtered_df.groupby(['Age']).sum()
        Filtered_group_df['Gamers In Category'] = Filtered_df.groupby(['Age']).size()
        Filtered_group_df['GAD_Ave'] = Filtered_group_df['GAD_T'] / Filtered_group_df['Gamers In Category'] #Higher = more anxiety
        Filtered_group_df['SWL_Ave'] = Filtered_group_df['SWL_T'] / Filtered_group_df['Gamers In Category'] #Lower = more anxiety
        Filtered_group_df['SPIN_Ave'] = Filtered_group_df['SPIN_T'] / Filtered_group_df['Gamers In Category'] #Higher = more anxiety
        Filtered_group_df['Average Result'] = ((Filtered_group_df['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - Filtered_group_df['SWL_Ave']) / SWL_TOTAL) + (Filtered_group_df['SPIN_Ave'] / SPIN_TOTAL)) / 3 * 100
        
        user_row = Filtered_group_df.loc[user_group]
        ave_res = user_row['Average Result']
        data = {'Categories':['Game Anxiety', 'No Game Anxiety'], 'Value': [ ave_res, 100-ave_res, ]}
        df = pd.DataFrame(data)
        fig = px.pie(df, values='Value', names='Categories',  color = 'Categories', color_discrete_map={'No Game Anxiety': 'gainsboro', 'Game Anxiety': 'mediumorchid'})
        fig.update_traces(hole=.6, hoverinfo="label+percent+name",  sort = False)
        graph5JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('Final.html', graph5JSON=graph5JSON, choices_gender = choices_gender, choices_playstyle = choices_playstyle, choices_reasons = choices_reasons)
        
    if request.method == 'POST':
        filter_age = int(request.form['age_input'])
        print(filter_age)
        filter_gender = request.form['gender_input']
        print(filter_gender)
        filter_reason = request.form['reason_input']
        print(filter_reason)
        filter_playstyle = request.form['playstyle_input']
        print(filter_playstyle)
        Filtering = GameAnxiety[['Age', 'Gender', 'GAD_T', 'SWL_T', 'SPIN_T']]
        Filtering['Playstyle'] = playstyle['Playstyle']
        Filtering['whyplay'] = Gamer_Reason['whyplay'] 
        choices_gender = ['Male', 'Female', 'Others']
        choices_playstyle = ['Singleplayer', 'Multiplayer - Offline', 'Multiplayer - Online', 'All of the above', 'Others']
        choices_reasons = ['having fun', 'improving', 'winning', 'relaxing', 'All of the above', 'Others']
        n_age_group = 5
        Filtering['Age'] = pd.cut(Filtering['Age'], n_age_group)
        
        for i in intervals:
            if filter_age in i:
                user_group = i
                break
        Filtered_df = Filtering[(Filtering['Age'] == user_group) & (Filtering['Gender'] == filter_gender) & (Filtering['whyplay'] == filter_reason) & (Filtering['Playstyle'] == filter_playstyle)]
        Filtered_group_df = Filtered_df.groupby(['Age']).sum()
        Filtered_group_df['Gamers In Category'] = Filtered_df.groupby(['Age']).size()
        Filtered_group_df['GAD_Ave'] = Filtered_group_df['GAD_T'] / Filtered_group_df['Gamers In Category'] #Higher = more anxiety
        Filtered_group_df['SWL_Ave'] = Filtered_group_df['SWL_T'] / Filtered_group_df['Gamers In Category'] #Lower = more anxiety
        Filtered_group_df['SPIN_Ave'] = Filtered_group_df['SPIN_T'] / Filtered_group_df['Gamers In Category'] #Higher = more anxiety
        Filtered_group_df['Average Result'] = ((Filtered_group_df['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - Filtered_group_df['SWL_Ave']) / SWL_TOTAL) + (Filtered_group_df['SPIN_Ave'] / SPIN_TOTAL)) / 3 * 100
        
        user_row = Filtered_group_df.loc[user_group]
        ave_res = user_row['Average Result']
        data = {'Categories':['Game Anxiety', 'No Game Anxiety'], 'Value': [ ave_res, 100-ave_res, ]}
        df = pd.DataFrame(data)
        fig = px.pie(df, values='Value', names='Categories',  color = 'Categories', color_discrete_map={'No Game Anxiety': 'gainsboro', 'Game Anxiety': 'mediumorchid'})
        fig.update_traces(hole=.6, hoverinfo="label+percent+name",  sort = False)
        graph5JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('Final.html', graph5JSON=graph5JSON, choices_gender = choices_gender, choices_playstyle = choices_playstyle, choices_reasons = choices_reasons)