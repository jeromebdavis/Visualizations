################################################################
#Get COVID tracking data through API and create charts by State#
################################################################

#Import python packages
import os
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import datetime as dt
import shutil

#Create state code dictionaries and strings for census data
state_code_dict = {"state":"code","AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11","FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56"}
state_code_string = "01,02,04,05,06,08,09,10,11,12,13,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,48,49,50,51,53,54,55,56"
state_code_list = ["01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53","54","55","56"]
state_list = ["National","Midwest","Northeast","South","West","AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
region_code_dict = {"State_Code":"Region","AK":"West","AL":"South","AZ":"West","AR":"South","CA":"West","CO":"West","CT":"Northeast","DE":"South","DC":"South","FL":"South","GA":"South","HI":"West","ID":"West","IL":"Midwest","IN":"Midwest","IA":"Midwest","KS":"Midwest","KY":"South","LA":"South","ME":"Northeast","MD":"South","MA":"Northeast","MI":"Midwest","MN":"Midwest","MS":"South","MO":"Midwest","MT":"West","NE":"Midwest","NV":"West","NH":"Northeast","NJ":"Northeast","NM":"West","NY":"Northeast","NC":"South","ND":"Midwest","OH":"Midwest","OK":"South","OR":"West","PA":"Northeast","RI":"Northeast","SC":"South","SD":"Midwest","TN":"South","TX":"South","UT":"West","VT":"Northeast","VA":"South","WA":"West","WV":"South","WI":"West","WY":"West"}
#state_list = ["NY","MD"]

#Delete current picture files
for stateID in state_list:
    if os.path.exists('covid_graph__'+stateID+'.png'):
        os.remove('covid_graph_'+stateID+'.png')

#Get COVID dataset
url_covid = 'https://covidtracking.com/api/v1/states/daily.json'
response = requests.get(url_covid)
formattedResponse = json.loads(response.text)[1:]
df_covid = pd.DataFrame(formattedResponse)

#Get census pop dataset 
apiKey = 'c04ab30e3be5b31ad7772fa15ad226d93cf1fa4b'
response = requests.get('https://api.census.gov/data/2019/pep/population?get=POP&for=state:'
                         +state_code_string+'&key='+apiKey)
formattedResponse = json.loads(response.text)
df_pop = pd.DataFrame(formattedResponse)
new_header = df_pop.iloc[0] #grab the first row for the header
df_pop = df_pop[1:] #take the data less the header row
df_pop.columns = new_header #set the header row as the df header
df_pop = df_pop.rename(columns={"state": "code"})

#Assign state abbreviations to pop dataset and merge with COVID dataset
state_code_df = pd.DataFrame.from_dict(state_code_dict, orient='index')
new_header = state_code_df.iloc[0] #grab the first row for the header
state_code_df = state_code_df[1:] #take the data less the header row
state_code_df.columns = new_header #set the header row as the df header
state_code_df['state'] = state_code_df.index
state_pop = pd.merge(df_pop, state_code_df, how='inner', on='code')
#state_pop = state_pop.drop(columns=['code'])
state_pop['POP'] = state_pop['POP'].astype(int)
df = pd.merge(df_covid, state_pop, how='left', on='state')

#Restrict values used in dataset
df = df[['date','state','positiveIncrease','negativeIncrease','deathIncrease',
         'hospitalizedCurrently','inIcuCurrently','POP']]

#Add dataset for regions and national and append to main dataset
region_code_df = pd.DataFrame.from_dict(region_code_dict, orient='index')
new_header = region_code_df.iloc[0] #grab the first row for the header
region_code_df = region_code_df[1:] #take the data less the header row
region_code_df.columns = new_header #set the header row as the df header
region_code_df = region_code_df.reset_index()
region_code_df = region_code_df.rename(columns={'index': 'state_code'})
region_df = pd.merge(df, region_code_df,  how='left', left_on=['state'], right_on = ['state_code'])
region_df = region_df.drop(columns=['state','state_code'])
region_df = region_df.rename(columns={'Region': 'state'})
region_df = region_df.groupby(['state','date']).sum()
region_df = region_df.reset_index()
national_df = region_df.copy()
national_df['state'] = 'National'
national_df = national_df.groupby(['state','date']).sum()
national_df = national_df.reset_index()
df = df.append(region_df)
df = df.append(national_df)

#Remove negative values in variables of interest
df['negativeIncrease']= df['negativeIncrease'].clip(lower=0)
df['positiveIncrease']= df['positiveIncrease'].clip(lower=0)
df['deathIncrease']= df['deathIncrease'].clip(lower=0)
df['hospitalizedCurrently']= df['hospitalizedCurrently'].clip(lower=0)
df['inIcuCurrently']= df['inIcuCurrently'].clip(lower=0)

#Calculate variables of interest
df['Negative_Pct'] = (df['negativeIncrease']) / df['POP'] * 100
df['Positive_Pct'] = (df['positiveIncrease']) / df['POP'] * 100
df['Death_Pct'] = (df['deathIncrease']) / df['POP'] * 100
df['Hospitalized_Pct'] = (df['hospitalizedCurrently']) / df['POP'] * 100
df['ICU_Pct'] = (df['inIcuCurrently']) / df['POP'] * 100

#Set covid graphs folder
Download_Folder = 'C:/Users/12407/Desktop/Education/Projects/COVID/Graphs_CT'

#Delete previous folder and create new blank folder  
try:
	shutil.rmtree(Download_Folder)
	print("Folder deletion succeeded")
except:
	print("Folder deletion failed")
try:
	os.mkdir(Download_Folder)
	print("Folder created succeeded")
except:
	print("Folder creation failed")

#Set current working directory to covid graphs folder
print('Current Working Directory' , os.getcwd())
os.chdir(Download_Folder)
print('New Working Directory' , os.getcwd())

#Set stateID
#state_list = ['MD','NY']

#Create charts
for stateID in state_list:
    state_df = df[df['state']==stateID]
    state_df = state_df.sort_values(by=['date'])
    state_df['date'] = state_df['date'].astype(str)
    state_df['date'] = (state_df['date'].str[0:4:1] + '-' + state_df['date'].str[4:6:1] + '-' 
            + state_df['date'].str[6:8:1])
    date_list = state_df['date'].astype('str')
    dates = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in date_list]
    fig = plt.figure(figsize=(18,9))    
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    #ax3 = fig.add_subplot(3, 1, 3)
    #fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle('Daily COVID statistics as percentage of population for ' + stateID, fontsize=16)
    #ax1 - negative and postive percent stack chart
    positive_rates = state_df['Positive_Pct'].astype('float')
    negative_rates = state_df['Negative_Pct'].astype('float')
    labels = ['Positive Tests', 'Negative Tests']
    ax1.stackplot(dates, positive_rates, negative_rates, labels=labels, colors=['yellow','green'])
    ax1.legend(loc='upper left')
    months = mdates.MonthLocator()
    months_fmt = mdates.DateFormatter('%b')
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
    ax1.xaxis.set_major_locator(months)
    ax1.xaxis.set_major_formatter(months_fmt)
    ax1.set_ylim(bottom=0.)
    ax1.grid(True)
    ax1.set_ylim(0, 0.8)
    ax1.set_yticks((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8))
    state_df['Positive_SMA_7'] = state_df.iloc[:,2].rolling(window=7).mean()
    state_df['Negative_SMA_7'] = state_df.iloc[:,3].rolling(window=7).mean()    
    state_df['Positive_Ratio_SMA_7'] = state_df['Positive_SMA_7']/state_df['Negative_SMA_7']
    positivity_rates = state_df['Positive_Ratio_SMA_7'].astype('float')
    ax1r = ax1.twinx()
    ax1r.plot(dates, positivity_rates, label='Positive/Negative Ratio (7 Day Average)', color='red')
    ax1r.legend(loc='upper right')
    ax1r.xaxis.set_major_locator(months)
    ax1r.xaxis.set_major_formatter(months_fmt)
    ax1r.set_ylim(bottom=0.)
    ax1r.grid(True)
    ax1r.set_ylim(0, 0.8)
    ax1r.set_yticks((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8))
    #ax2 - deaths and hospitalizations percent line chart
    death_rates = state_df['Death_Pct'].astype('float')
    hospitalized_rates = state_df['Hospitalized_Pct'].astype('float')
    icu_rates = state_df['ICU_Pct'].astype('float')
    ax2.plot(dates, icu_rates, label='Currently in ICU', color='yellow')
    ax2.plot(dates, hospitalized_rates, label='Currently Hospitalized', color='green')
    ax2.set_ylim(0, 0.10)
    ax2.set_yticks((0, 0.02, 0.04, 0.06, 0.08, 0.10))
    ax2.legend(loc='upper left')
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))
    ax2.xaxis.set_major_locator(months)
    ax2.xaxis.set_major_formatter(months_fmt)
    ax2.set_ylim(bottom=0.)
    ax2r = ax2.twinx()
    ax2r.plot(dates, death_rates, label='Deaths', color='red')
    ax2r.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=3))
    ax2r.xaxis.set_major_locator(months)
    ax2r.xaxis.set_major_formatter(months_fmt)
    ax2r.set_ylim(bottom=0.)
    ax2r.legend(loc='upper right')
    ax2r.grid(True)
    ax2r.set_ylim(0, 0.005)
    ax2r.set_yticks((0, 0.001, 0.002, 0.003, 0.004, 0.005)) 
    plt.savefig('covid_graph_' + stateID + '.png', format='png', bbox_inches='tight')
    plt.close()