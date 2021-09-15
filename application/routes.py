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

Gamer_Age = GameAnxiety[['Age', 'GAD_T', 'SWL_T', 'SPIN_T']]
n_age_group = 5
age_max = Gamer_Age['Age'].max()
age_min = Gamer_Age['Age'].min()
age_n_range = (age_max - age_min) / n_age_group
Gamer_Age['Age'] = pd.cut(Gamer_Age['Age'], n_age_group)

Gamer_Age_Total = Gamer_Age.groupby(['Age']).sum()
Gamer_Age_Total['Gamers In Category'] = Gamer_Age.groupby(['Age']).size()
Gamer_Age_Total['GAD_Ave'] = Gamer_Age_Total['GAD_T'] / Gamer_Age_Total['Gamers In Category'] #Higher = more anxiety
Gamer_Age_Total['SWL_Ave'] = Gamer_Age_Total['SWL_T'] / Gamer_Age_Total['Gamers In Category'] #Lower = more anxiety
Gamer_Age_Total['SPIN_Ave'] = Gamer_Age_Total['SPIN_T'] / Gamer_Age_Total['Gamers In Category'] #Higher = more anxiety
Gamer_Age_Total['Average Result'] = ((Gamer_Age_Total['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - Gamer_Age_Total['SWL_Ave']) / SWL_TOTAL) + (Gamer_Age_Total['SPIN_Ave'] / SPIN_TOTAL)) / 3 * 100

user_age = 19
@app.route('/')
def index():
    return render_template('index.html', title = "Home Page")

@app.route('/ageGroup', methods=['POST'])
def textInput():
    text = int(request.form['text'])
    
    user_age = text
    age_groups = list(Gamer_Age_Total.index)
    for group in age_groups:
        if user_age in group:
            user_group = group

    user_row = Gamer_Age_Total.loc[user_group]
    ave_res = user_row['Average Result']
    data = {'Categories':['Game Anxiety', 'No Game Anxiety'], 'Value': [ ave_res, 100-ave_res, ]}
    df = pd.DataFrame(data)
    fig = px.pie(df, values='Value', names='Categories',  color = 'Categories', color_discrete_map={'No Game Anxiety': 'gainsboro', 'Game Anxiety': 'mediumorchid'})
    fig.update_traces(hole=.6, hoverinfo="label+percent+name",  sort = False)

    graph1JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('Age Group.html', graph1JSON=graph1JSON)

@app.route('/ageGroup')
def ageGroup():
    age_groups = list(Gamer_Age_Total.index)
    for group in age_groups:
        if user_age in group:
            user_group = group

    user_row = Gamer_Age_Total.loc[user_group]
    ave_res = user_row['Average Result']
    data = {'Categories':['Game Anxiety', 'No Game Anxiety'], 'Value': [ ave_res, 100-ave_res, ]}
    df = pd.DataFrame(data)
    fig = px.pie(df, values='Value', names='Categories',  color = 'Categories', color_discrete_map={'No Game Anxiety': 'gainsboro', 'Game Anxiety': 'mediumorchid'})
    fig.update_traces(hole=.6, hoverinfo="label+percent+name",  sort = False)

    graph1JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Age Group.html', graph1JSON=graph1JSON)

@app.route('/Gender')
def Gender():
    GamerGender = GameAnxiety[['Gender', 'GAD_T', 'SWL_T', 'SPIN_T']]
    GamerGender_total = GamerGender.groupby(['Gender']).sum()
    GamerGender_total['Gamers in Category'] = GamerGender.groupby(['Gender']).size()
    GamerGender_total['GAD_Ave'] = GamerGender_total['GAD_T'] / GamerGender_total['Gamers in Category']
    GamerGender_total['SWL_Ave'] = GamerGender_total['SWL_T'] / GamerGender_total['Gamers in Category']
    GamerGender_total['SPIN_Ave'] = GamerGender_total['SPIN_T'] / GamerGender_total['Gamers in Category']
    GamerGender_total['Average Result'] = ((GamerGender_total['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - GamerGender_total['SWL_Ave']) / SWL_TOTAL) + (GamerGender_total['SPIN_Ave'] / SPIN_TOTAL)) / 3 * 100
    
    fig = px.pie(GamerGender_total, values = 'Average Result', names = GamerGender_total.index, color = GamerGender_total.index, color_discrete_map={'Other' : '#B399D4', 'Male': '#96B9D0', 'Female': '#EBA7AC'})
    graph2JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Gender.html', graph2JSON=graph2JSON)

@app.route('/Playstyle')
def Playstyle():
    playstyle = GameAnxiety[['Playstyle', 'GAD_T', 'SWL_T', 'SPIN_T']]
    playstyle_Total = playstyle.groupby(['Playstyle']).sum()
    playstyle_Total['Gamers in Category'] = playstyle.groupby(['Playstyle']).size()

    playstyle_df = playstyle_Total.nlargest(4, columns=['Gamers in Category'])

    playstyle_df.loc[len(playstyle_df)] = [playstyle_Total.drop(playstyle_df.index)['GAD_T'].sum(), playstyle_Total.drop(playstyle_df.index)['SWL_T'].sum(), playstyle_Total.drop(playstyle_df.index)['SPIN_T'].sum(), playstyle_Total.drop(playstyle_df.index)['Gamers in Category'].sum()]
    playstyle_df = playstyle_df.rename(index={4: 'Others'})

    playstyle_df['GAD_Ave'] = playstyle_df['GAD_T'] / playstyle_df['Gamers in Category']
    playstyle_df['SWL_Ave'] = playstyle_df['SWL_T'] / playstyle_df['Gamers in Category']
    playstyle_df['SPIN_Ave'] = playstyle_df['SPIN_T'] / playstyle_df['Gamers in Category']
    playstyle_df['Average_Result'] = round(((playstyle_df['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - playstyle_df['SWL_Ave']) / SWL_TOTAL) + (playstyle_df['SPIN_Ave'] / SPIN_TOTAL)) / 3, 4)

    playstyle_df.sort_values(by=['Gamers in Category'], ascending = False)

    Play_Style = list(playstyle_df.index)
    Average_resultPS =  playstyle_df['Average_Result']
    style_of_play = plt.barh(Play_Style, Average_resultPS)
    fig = px.bar(style_of_play, Average_resultPS, Play_Style, text=[f'{i:.2f}%' for i in Average_resultPS*100],
            color = Play_Style, color_discrete_map={
                "Multiplayer - Offline": "#6F5F90",
                "Multiplayer - Online": "#FF7B89",
                "Singleplayer": "#8A5082",
                "All of the above": "#758EB7",
                "Others": "#A5CAD2"}, 
                labels={
                     "x": "Average Results (in percentage) for each playstyle",
                     "y": "Playstyle"
                 }, title="How does the playstyle of the gamer affect anxiety?", orientation='h', width=800, height = 350)
    fig.update_layout(showlegend=False)
    fig.layout.xaxis.tickformat = '0.00%'
    fig.update_layout(xaxis_range=[0,1])
    graph3JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('Playstyle.html', graph3JSON=graph3JSON)

@app.route('/Reason')
def Reason():
    Gamer_Reason = GameAnxiety[['whyplay', 'GAD_T', 'SWL_T', 'SPIN_T']]
    Gamer_Reason_Total = Gamer_Reason.groupby(['whyplay']).sum()
    Gamer_Reason_Total['Gamers In Category'] = Gamer_Reason.groupby(['whyplay']).size()
    #Gamer_Reason_Total.loc[Gamer_Reason_Total['Gamers In Category'] < 2, 'whyplay'] = "Others"
    Gamer_Reason_df = Gamer_Reason_Total.nlargest(5, columns=['Gamers In Category'])

    Gamer_Reason_df.loc[len(Gamer_Reason_df)] = [Gamer_Reason_Total.drop(Gamer_Reason_df.index)['GAD_T'].sum(), Gamer_Reason_Total.drop(Gamer_Reason_df.index)['SWL_T'].sum(), Gamer_Reason_Total.drop(Gamer_Reason_df.index)['SPIN_T'].sum(), Gamer_Reason_Total.drop(Gamer_Reason_df.index)['Gamers In Category'].sum()]
    Gamer_Reason_df = Gamer_Reason_df.rename(index={5: 'Others'})

    Gamer_Reason_df['GAD_Ave'] = Gamer_Reason_df['GAD_T'] / Gamer_Reason_df['Gamers In Category']
    Gamer_Reason_df['SWL_Ave'] = Gamer_Reason_df['SWL_T'] / Gamer_Reason_df['Gamers In Category']
    Gamer_Reason_df['SPIN_Ave'] = Gamer_Reason_df['SPIN_T'] / Gamer_Reason_df['Gamers In Category']
    Gamer_Reason_df['Average Result'] = round(((Gamer_Reason_df['GAD_Ave']/GAD_TOTAL) + ((SWL_TOTAL - Gamer_Reason_df['SWL_Ave']) / SWL_TOTAL) + (Gamer_Reason_df['SPIN_Ave'] / SPIN_TOTAL)) / 3 , 4)

    Playing_reasons = list(Gamer_Reason_df.index)
    Average_result =  Gamer_Reason_df['Average Result']
    reason_for_playing = plt.barh(Playing_reasons, Average_result)

    df = px.data.tips()
    fig = px.bar(reason_for_playing, Average_result, Playing_reasons, text=[f'{i:.2f}%' for i in Average_result*100], 
                color = Playing_reasons, color_discrete_map={
                    "having fun": "#FF7B89",
                    "improving": "#8A5082",
                    "winning": "#6F5F90",
                    "relaxing": "#758EB7",
                    "All of the above": "#A5CAD2",
                    "Others": "#a0b0cf"}, 
                    labels={
                        "x": "Average Results (in percentage) for each reason for playing",
                        "y": "Reasons for playing"
                    }, title="How does the reason for playing affect the gamer’s anxiety levels?", orientation='h', width=800, height = 400)
    fig.update_layout(showlegend=False)
    fig.layout.xaxis.tickformat = '0.00%'
    fig.update_layout(xaxis_range=[0,1])
    graph4JSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('Reason.html', graph4JSON=graph4JSON)

@app.route('/Final', methods = ['GET', 'POST'])
def Final():
    if request.method == 'GET':
        filter_age = 30
        filter_gender = "Male"
        filter_reason = "having fun"
        filter_playstyle = "Singleplayer"
        
        Filtering = GameAnxiety[['Age', 'Gender', 'whyplay', 'Playstyle',  'GAD_T', 'SWL_T', 'SPIN_T']]
        choices_gender = ['Male', 'Female', 'Others']
        choices_playstyle = ['Singleplayer', 'Multiplayer - Offline', 'Multiplayer - Online', 'All of the above', 'Others']
        choices_reasons = ['having fun', 'improving', 'winning', 'relaxing', 'All of the above', 'Others']
        n_age_group = 5
        Filtering['Age'] = pd.cut(Filtering['Age'], n_age_group)
        age_groups = list(Gamer_Age_Total.index)
        for i in age_groups:
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
        Filtering = GameAnxiety[['Age', 'Gender', 'whyplay', 'Playstyle',  'GAD_T', 'SWL_T', 'SPIN_T']]
        choices_gender = ['Male', 'Female', 'Others']
        choices_playstyle = ['Singleplayer', 'Multiplayer - Offline', 'Multiplayer - Online', 'All of the above', 'Others']
        choices_reasons = ['having fun', 'improving', 'winning', 'relaxing', 'All of the above', 'Others']
        n_age_group = 5
        Filtering['Age'] = pd.cut(Filtering['Age'], n_age_group)
        age_groups = list(Gamer_Age_Total.index)
        for i in age_groups:
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


