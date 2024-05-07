import streamlit as st
import pandas as pd
from helper import add_logo, haversine
import plotly.express as px
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly"

st.set_page_config(page_title="Bedroom Size", 
                   page_icon="🛌🏼",
                   layout="wide")

st.markdown("# Generate maps from Coordinate")

# DATASET
# DEFINISIKAN DATA DAN METRIKS
FOLDER_PATH = 'data'
file_name = st.selectbox(
    'Pilih sumber dataset',
    (os.listdir(FOLDER_PATH)))
df = pd.read_csv(f'{FOLDER_PATH}/{file_name}').rename({
                                                'reviewsCount': 'review_count',
                                                'listing_id': 'id',
                                                'lat':'coordinate.latitude',
                                                'long':'coordinate.longitude',
                                                'review': 'review_rating'
                                            }, axis=1)
df['id'] = df['id'].apply(int)
df['review_count'] = df['review_count'].fillna(0)
# SIDEBAR
# st.sidebar.header("Sentiment")
add_logo("https://upload.wikimedia.org/wikipedia/commons/archive/c/ce/20210909091155%21Twitter_Logo.png",40)



# sentimen
a11, a12, a13 = st.columns(3)

# st.info("Masukkan titik lokasi latitude dan longitude", icon="ℹ")
with a11:  
    # File uploader widget
    prop_lat = st.text_input("Latitude")

with a12: 
    prop_lon = st.text_input("Longitude")

with a13: 
    max_dist = st.number_input("Maximum Distance", min_value=0.1, value=3.0)

if st.button("Generate Map"):
    fig = go.Figure()

    fig.update_layout(
        titlefont = dict(size=20, color='black'),
        title_text='Airbnb BR Size & Review Count Bubble Mapbox', title_x=0.5,
        autosize=True,
        mapbox=dict(
            bearing=0,
            center=dict(
                lat=-8.4095,
                lon=115.1889
            )
        ),
        mapbox_style= 'carto-positron',
        width=1080,
        height=600,
        margin=dict(
            l=20,
            r=20,
            b=20,
            t=50
        )
    )

    # Data with latitude/longitude and values
    if df['review_count'].nunique() > 1:
        size = 'review_count'
    else:
        size = None

    map_scatter = px.scatter_mapbox(df, lat = 'coordinate.latitude', lon = 'coordinate.longitude',
                            size=size, size_max=30,
                            color = 'bedroom',
                            zoom=10,
                            hover_name="id",
                            hover_data=["bedroom", "review_rating", "review_count"])


    fig.add_traces(list(map_scatter.select_traces()))
    fig.update_layout(coloraxis={'colorbar':{'title': {'text': 'Num of BR'}},
                                'cmin':0, 'cmax':10},
                    colorscale_sequential=[[0, 'rgb(255,255,255)'],
                                            [0.1, 'rgb(0,255,0)'],
                                            [0.2, 'rgb(255,255,0)'],
                                            [0.3, 'rgb(0,0,255)'],
                                            [0.4, 'rgb(0,255,255)'],
                                            [0.5, 'rgb(255,0,255)'],
                                            [0.6, 'rgb(192,192,192)'],
                                            [0.7, 'rgb(128,0,0)'],
                                            [0.8, 'rgb(0,128,0)'],
                                            [0.9, 'rgb(128,0,128)'],
                                            [1, 'rgb(0,0,0)']],
                    )

    if prop_lat != 0 and prop_lon !=0:
        fig.add_scattermapbox(lat = [prop_lat]
                            ,lon = [prop_lon]
                            # ,hoverinfo = 'Property'
                            ,marker_size = 30
                            ,marker_color = 'red'
                            # ,marker_symbol = 'star'
                            ,showlegend = False
                            ,opacity=1
                            )

    st.plotly_chart(fig, theme=None, use_container_width=True)

    if prop_lat != "" and prop_lon !="" and max_dist != 0:
        st.header("Nearby Property")

        df['distance_to_curr_loc'] = df.apply(lambda x: haversine(float(prop_lat), float(prop_lon), x['coordinate.latitude'], x['coordinate.longitude']), axis=1)
        df['link'] = df.apply(lambda x: f"https://www.airbnb.com/rooms/{x['id']}", axis=1)

        df_agg = df[df['distance_to_curr_loc']<3].groupby(['bedroom']).agg({
            "review_rating" : "mean",
            "review_count" : "sum",
            "id" : "count"
        }).reset_index()
        
        fig = px.bar(df_agg[df_agg['bedroom']>0], x="bedroom", y="review_count", text_auto=True)

        fig.update_layout(
            titlefont = dict(size=20, color='black'),
            title_text=f'Review Totals of Nearby Properties (within ~{max_dist} km) Based on BR Size', title_x=0.5,
            autosize=True,
            width=1080,
            height=600,
            # margin=dict(
            #     l=20,
            #     r=20,
            #     b=20,
            #     t=50
            # )
        )
        st.plotly_chart(fig, theme=None, use_container_width=True)

        st.dataframe(df[df['distance_to_curr_loc']<max_dist].loc[:,
                             ["listing_name",
                            "roomTypeCategory",
                            "bedroom",
                            "Pool",
                            "Kitchen",
                            "review_count",
                            "review_rating",
                            "distance_to_curr_loc",
                            "link"
                            ]],
                )