import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import numpy as np


st.title('NBA Stats Explorer')

st.markdown("""
This app performs simple webscraping of NBA player stats data.
* **Python libraries:** BeautifulSoup, pandas, streamlit, numpy, matplotlib, plotly, requests
* **Data source:** [Basketball Reference](https://www.basketball-reference.com/).
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1980,2021))))

@st.cache
def load_data(year):
    # Load general data
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    df = pd.read_html(url)[0]
    df.drop(columns='Rk', inplace=True)
    df.drop(df[df.Player == 'Player'].index, inplace=True)
    df.fillna(0, inplace=True)
    numeric_features = df.columns.drop(['Player', 'Pos', 'Tm'])
    df[numeric_features] = df[numeric_features].applymap(lambda x: pd.to_numeric(x))
    df = df.drop_duplicates(subset=['Player'], keep='last')
    
    return df


def load_mvp(year):
    # Load MVP data
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    mvp_link = soup.find(id='info').find_all('p')[3].find('a').attrs['href']
    mvp_page = requests.get('https://www.basketball-reference.com' + mvp_link)
    mvp_soup = BeautifulSoup(mvp_page.content, 'html.parser')
    
    return mvp_soup
    


playerstats = load_data(selected_year)
mvp_data = load_mvp(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats.Tm.unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['C', 'PF', 'SG', 'PG', 'SF', 'PF-SF', 'PF-C', 'SF-SG', 'SF-C',
       'SF-PF', 'SG-SF', 'C-PF', 'SG-PG', 'PG-SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

if selected_team != [] and selected_pos != []:
    # Filtering data
    df_filtered = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

    st.header('Display Player Stats of Selected Team(s)')
    st.write('Data Dimension: ' + str(df_filtered.shape[0]) + ' rows and ' + str(df_filtered.shape[1]) + ' columns.')


    st.dataframe(df_filtered.set_index('Player').style.set_precision(2).highlight_max(color = 'lightgreen', axis = 0))

    # Show MVP
    mvp_picture = mvp_data.find(class_='players').find('img')['src']
    mvp_name = mvp_data.find(class_='players').find('span').text
    st.header("Season's MVP:")
    st.markdown(f'''
                **{mvp_name}**''')
    st.image(mvp_picture)

    mvp_stats = playerstats[playerstats.Player.str.contains(mvp_name)]
    st.dataframe(mvp_stats.set_index('Player').style.set_precision(2))


    # Minimum games played to be considered is 70% of Team's games according to NBA's website
    min_games = 0.7 * df_filtered.G.max()
    df_min_games = df_filtered[df_filtered.G > min_games]


    # 2pts analysis
    # Removing outlier values 
    df_2pts = df_min_games[(df_min_games['2PA'] > np.percentile(df_min_games['2PA'], 25))]
    fig_2pts = px.scatter(df_2pts, x = '2PA', y = '2P%', size = 'PTS', hover_name = 'Player', 
                    color = 'Pos', title = '2pts analysis',
                    labels={
                        "2PA": "2 pts attempts",
                        "2P%": "2 pts %",
                        "Pos": "Position"
                    })
    fig_2pts.add_vline(x = np.mean(df_2pts['2PA']), annotation_text = 'Average 2-pts attempts')
    fig_2pts.add_hline(y = np.mean(df_2pts['2P%']), annotation_text = 'Average 2-pts %')

    if st.button('2pts analysis'):
        st.plotly_chart(fig_2pts, use_container_width=True)

    # 3pts analysis
    # Removing outlier values 
    df_3pts = df_min_games[(df_min_games['3PA'] > np.percentile(df_min_games['3PA'], 25))]
    fig_3pts = px.scatter(df_3pts, x = '3PA', y = '3P%', size = 'PTS', hover_name = 'Player',
                        color = 'Pos', title = '3pts analysis',
                        labels={
                        "3PA": "3 pts attempts",
                        "3P%": "3 pts %",
                        "Pos": "Position"
                    })
    fig_3pts.add_vline(x = np.mean(df_3pts['3PA']), annotation_text = 'Average 3-pts attempts')
    fig_3pts.add_hline(y = np.mean(df_3pts['3P%']), annotation_text = 'Average 3-pts %')

    if st.button('3pts analysis'):
        st.plotly_chart(fig_3pts, use_container_width=True)
        
    # Free throws analysis
    # Removing outlier values 
    df_ft = df_min_games[(df_min_games['FTA'] > np.percentile(df_min_games['FTA'], 25) )]
    fig_free_throws = px.scatter(df_ft, x = 'FTA', y = 'FT%', size = 'PTS', hover_name = 'Player', 
                    color = 'Pos', title = 'Free throws analysis',
                    labels={
                        "FTA": "Free throws attempts",
                        "FT%": "Free throws %",
                        "Pos": "Position"
                    })
    fig_free_throws.add_vline(x = np.mean(df_ft['FTA']), annotation_text = 'Average Free Throws Attemps')
    fig_free_throws.add_hline(y = np.mean(df_ft['FT%']), annotation_text = 'Average Free Throws %')

    if st.button('Free throws analysis'):
        st.plotly_chart(fig_free_throws, use_container_width=True)
        
        
    # Rebounds analysis
    # Removing outlier values 
    df_rebounds = df_min_games[(df_min_games['TRB'] > np.percentile(df_min_games['TRB'], 25) )]      
    fig_rebounds = px.scatter(df_rebounds, x = 'DRB', y = 'ORB', size = 'TRB', hover_name = 'Player', 
                    color = 'Pos', title = 'Rebounds analysis',
                    labels={
                        "DRB": "Defensive Rebounds",
                        "ORB": "Offensive Rebounds",
                        "Pos": "Position"
                    })
    fig_rebounds.add_vline(x = np.mean(df_rebounds['DRB']), annotation_text = 'Average Defensive Rebounds')
    fig_rebounds.add_hline(y = np.mean(df_rebounds['ORB']), annotation_text = 'Average Offensive Rebounds')

    if st.button('Rebounds analysis'):
        st.plotly_chart(fig_rebounds, use_container_width=True)
        
    st.write('Note: All analysis were performed with statistically relevant data by applying minimum occurrence thresholds.')
else:
    st.info('You need to select at least one Position and one Team to get started')        