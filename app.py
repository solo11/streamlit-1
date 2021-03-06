from django.db import DatabaseError
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vRUZasAQKQ5TdmeDuaSmB4RvMoK1mkjhaZGFp_2a5f549X9BOpbeO3tIo3BqRltfgHnjbsKo3E12r_-/pub?output=csv")

st.title("Hello world!")

st.markdown("### Welcome to my dashboard!!")

@st.cache(persist=True)
def data_load(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["CRASH_DATE","CRASH_TIME"]], dtype={"ZIP_CODE" : "string"})
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase = lambda x : str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'},inplace=True)
    data.style.format({
        "date/time" : lambda t : t.strftime("%B %d, %Y, %r")
    })
    return data

data = data_load(100000)

data_org = data



st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collisions",0,19)
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("How many collisions occured during a given time of day?")
hour = st.slider("Hour to look at", 0,23)
data = data[data["date/time"].dt.hour == hour]

midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour,hour+1))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude" : midpoint[0],
        "longitude" : midpoint[1],
        "zoom" : 11,
        "pitch": 50,
    },
    layers= [
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time','latitude','longitude']],
            get_position=['longitude','latitude'],
            radius = 100,
            extruded= True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000]
        )
    ]
))

st.markdown("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1) % 24))
filtered_data = data[
    (data['date/time'].dt.hour >= hour ) & (data['date/time'].dt.hour <  (hour+1 ))
    ]
hist = np.histogram(filtered_data['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data=   ['minute','crashes'], height=400)

st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type people',['Pedestrians','Cyclists','Motorist'])

if select == 'Pedestrians':
    st.write(data_org.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(data_org.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])

elif select == 'Motorist':
    st.write(data_org.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])        



if st.checkbox("Show raw data",False):
    st.subheader('Raw Data')
    st.write(data)