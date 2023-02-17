

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Reduce the loading time.
@st.cache(allow_output_mutation=True)
def get_data(filename):
    read_data=pd.read_csv(filename)
    
    return read_data
    

# Creating section in the webpage
header = st.container()

 
# DATA IMPORT AND DATA PROCESSING same as in Data Manipulation Jupter Notebook. Can directly skip to the Webpage 
# DATA IMPORT
# Port data
portcalls_file_path = "Data/Maritime data/US_PortCalls_S_ST202209220924_v1.csv"
df_port = get_data(portcalls_file_path) # Reading the port data into 'df_ports'

# Port calls data
portcalls_file_path_new = "Data/Maritime data/US_PortCallsArrivals_S_ST202209220927_v1.csv"
df_port_calls = get_data(portcalls_file_path_new)

# Covid Data
covid_file_path = "Data\COVID data\WHO-COVID-19-global-data.csv"
df_covid = get_data(covid_file_path) # Reading the covid data into 'df_covid'




# DATA PROCESSING:
# Removing all the unnecessary fields from the data set.
df_port = df_port.drop(columns=['Period Label','Frequency', 'Frequency Label', 'Economy', 
                                'CommercialMarket', 'Median time in port (days) Footnote',
                                'Average age of vessels Footnote', 'Average size (GT) of vessels Footnote',
                                'Maximum size (GT) of vessels Footnote',
                                'Average cargo carrying capacity (dwt) per vessel Footnote',
                                'Maximum cargo carrying capacity (dwt) of vessels Footnote',
                                'Average container carrying capacity (TEU) per container ship Footnote',
                                'Maximum container carrying capacity (TEU) of container ships Footnote'])

# Renaming the column names to be easily recognizable.
df_port.rename(columns = {'Economy Label': 'country', 'CommercialMarket Label': 'Vessel_Type', }, inplace=True)

#The time frame in the Period column is modified to match with the date column of the covid data.
date_change=[]
for row in df_port['Period']:
        if row == '2018S01' :   
            date_change.append(datetime(2018,7,31))
        elif row == '2018S02':  
            date_change.append(datetime(2019,1,31))
        elif row == '2019S01':  
            date_change.append(datetime(2019,7,31))
        elif row == '2019S02':  
            date_change.append(datetime(2020,1,31))
        elif row == '2020S01':  
            date_change.append(datetime(2020,7,31))
        elif row == '2020S02':  
            date_change.append(datetime(2021,1,31))
        elif row == '2021S01':  
            date_change.append(datetime(2021,7,31))
        elif row == '2021S02':  
            date_change.append(datetime(2022,1,31))
        elif row == '2022S01':  
            date_change.append(datetime(2022,7,31)) 
        else:           
            date_change.append('Not_Rated')

# Period column is removed as it has no importance in future processes and column 'date' is added
df_port['date'] = date_change


# Port Calls Data
df_port_calls['Period Label'] = df_port_calls['Period Label'].str.replace('   ','-')
df_port_calls = df_port_calls.drop(columns=['Period', 'Frequency', 'Frequency Label', 'Economy', 
                                            'CommercialMarket', 'Number of port calls Footnote',])
df_port_calls.rename(columns = {'Economy Label': 'country', 'CommercialMarket Label': 'Vessel_Type', }, inplace=True)

date_change=[]
for row in df_port_calls['Period Label']:
        if row == 'S1-2018' :   
            date_change.append(datetime(2018,7,31))
        elif row == 'S2-2018':   
            date_change.append(datetime(2019,1,31))
        elif row == 'S1-2019':  
            date_change.append(datetime(2019,7,31))
        elif row == 'S2-2019':  
            date_change.append(datetime(2020,1,31))
        elif row == 'S1-2020':  
            date_change.append(datetime(2020,7,31))
        elif row == 'S2-2020':  
            date_change.append(datetime(2021,1,31))
        elif row == 'S1-2021':  
            date_change.append(datetime(2021,7,31))
        elif row == 'S2-2021':  
            date_change.append(datetime(2022,1,31))
        elif row == 'S1-2022':  
            date_change.append(datetime(2022,7,31))
        else:           
            date_change.append('Not_Rated')

df_port_calls = df_port_calls.drop(columns=['Period Label'])
df_port_calls['date'] = date_change
df_port_calls

# Covid Data
df_covid = df_covid.rename({
    'Date_reported': 'date',
    'Country': 'country',
    'New_cases': 'new_cases',
    'Cumulative_cases': 'cumulative_cases'}, axis=1) 
df_covid = df_covid.drop(labels=[
        'New_deaths', 
        'Cumulative_deaths', 
        'Country_code', 
        'WHO_region'], axis=1)

for i in range(len(df_covid)):
        k=df_covid.iloc[i,0].split('/')
        df_covid.iloc[i,0]=datetime(int(k[0]),int(k[1]),int(k[2]))

df_covid_new = (df_covid.groupby(['country', pd.Grouper(key='date', freq='6M')]).sum().reset_index()) # gives the sum value of the new cases.
    

# Merging of port data and the covid data
port_covid = pd.merge(df_port, df_covid_new, on=['country','date'], how='outer')
df_combined2 = pd.merge(df_port_calls,df_covid_new,on=['country','date'], how='outer')# merging port call and covid data




# Webpage display
with header:  # accesing the section for presenting the info
    st.title('Impact of covid on various vessel operations across different countries')

    
    # Creating a dynamic multiselect box for user to choose countries from
    country_options = port_covid['country'].unique() #converting unqiue values to list,
    # [Note:(do not use tolist() if it's already a list), in our case, it's already a list,
    # otherwise it would be df_combined['country'].tolist().unique())
    # This list will be used as options for multiselect for user to choose which country data he/she wants to see
    
    # Creating a multiselect toggle option for user to choose from country_options and setting the default option as world
    country= st.multiselect('Which country data would you like to see',country_options,['Netherlands']) 
    
    
    # Creating a dynamic dropdown box for user to choose vessel types from
    vessel_options = port_covid['Vessel_Type'].unique()
    vessel = st.selectbox('Which Vessel data would you like to see',options =vessel_options,index=0)
    # Index sets the default value at the index of the list that will be displayed if nothing is selected.
    
    
    
    # Filtering the data according to user's choice in both options
    df=port_covid[(port_covid['country'].isin(country)) & (port_covid['Vessel_Type']==vessel)]
    
    # Filtering the data according to user's choice in both options in port calls dataset
    dp=df_combined2[(df_combined2['country'].isin(country)) & (df_combined2['Vessel_Type']==vessel)]
    
   # Creating  different containers inside the graph container plot various graphs with subheadings.
    median_time=st.container()
    avg_age=st.container()
    carry_capacity=st.container()
    avg_size=st.container()
    port_calls=st.container()


# Accessing the containers to create its subheadings and columns.
with median_time:
    st.subheader("1. Impact of covid on time spent by vessels in ports:")
    median_col, cm_col =st.columns(2)

with avg_age:
    st.subheader("2. Impact of covid on average size of vessels:")
    age_col, ca_col =st.columns(2)

    
with carry_capacity:
    st.subheader("3. Impact of covid on average cargo carrying capacity of vessels:")
    cap_col, cp_col =st.columns(2)

with avg_size:
    st.subheader("4. Impact of covid on average size of vessels:")
    size_col, cs_col =st.columns(2)
     
with port_calls:
    st.subheader("5. Impact of covid on number of port calls:")
    call_col, cl_col =st.columns(2)

    
   

    
    
# Accessing the containers to plot the port and covid in respective columns
with median_time:
    with median_col:
        fig = px.line(df,x='date',y='Median time in port (days)',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    with cm_col:
        fig = px.line(df,x='date',y='new_cases',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    
with avg_age:
    with age_col:
        fig = px.line(df,x='date',y='Average age of vessels',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    with ca_col:
        fig = px.line(df,x='date',y='new_cases',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)

with carry_capacity:
    with cap_col:
        fig = px.line(df,x='date',y='Average cargo carrying capacity (dwt) per vessel',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    with cp_col:
        fig = px.line(df,x='date',y='new_cases',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
        
with avg_size:
    with size_col:
        fig = px.line(df,x='date',y='Average size (GT) of vessels',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    with cs_col:
        fig = px.line(df,x='date',y='new_cases',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    
with port_calls:     
    with call_col:
        fig = px.line(dp,x='date',y='Number of port calls',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)
    with cl_col:
        fig = px.line(df,x='date',y='new_cases',color='country',markers=True)
        fig.update_layout(width=400)
        st.write(fig)

# to run on the webpage : go to cmd go to the file path where this file is located using command 'cd'
#then type streamlit run port1.1.py