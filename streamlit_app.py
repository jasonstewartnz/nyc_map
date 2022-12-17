import streamlit as st
import pandas as pd
import numpy as np
from snowflake import connector 



default_focus_coordinates = (-74.00296211242676,40.72143702499928)
default_distance = 2000


    
    
def get_coordinates(distance, focus_coordinates):
    query_sql = f"""
        SELECT 
            NAME,
            AMENITY,
            COALESCE(ADDR_HOUSENAME || ' ' ,'') || COALESCE(ADDR_HOUSENUMBER || ' ' ,'') || COALESCE(ADDR_STREET,'') as location,
            -- COORDINATES,    
            CASE WHEN ST_NUMPOINTS(COORDINATES) = 1
                THEN COORDINATES 
                ELSE ST_CENTROID(COORDINATES)
                END as primary_coordinate,
            ST_X(primary_coordinate) as lon,
            ST_Y(primary_coordinate) as lat,
            st_distance(ST_POINT({focus_coordinates[0]},{focus_coordinates[1]}), primary_coordinate) as distance_away_m
        FROM OPENSTREETMAP_NEW_YORK.NEW_YORK.V_OSM_NY_AMENITY_SUSTENANCE
        WHERE ST_DWITHIN(ST_POINT({focus_coordinates[0]},{focus_coordinates[1]}),
               CASE WHEN ST_NUMPOINTS(COORDINATES) = 1
                THEN COORDINATES 
                ELSE ST_CENTROID(COORDINATES)
                END
               ,{distance});    
    """    
    
    # connect to snowflake
    sf_conn = connector.connect(**st.secrets["snowflake"])

    # put the dafta into a dataframe
    nyc_locations = pd.read_sql(query_sql, sf_conn)
    
    return nyc_locations

def init_app_elements():
    st.title( 'NYC Street Map' )
    
    distance = st.number_input('Distance (m)', min_value=100, max_value=5000, value=default_distance, step=100, format='%u', on_change=get_coordinates, key="distance_input" )
    
    st.header( f'Locations within {distance:.0f}m of location X', key='header' )
    
    nyc_locations = get_coordinates(distance, default_focus_coordinates)
                                    
    st.map(nyc_locations, key='map')
    
    st.dataframe(nyc_locations.loc[:,['NAME','AMENITY','LOCATION','DISTANCE_AWAY_M']], key='location_list')
    
def update_app():
    distance = st.session_state['distance_input'].value
    focus_coordinates = default_coordinates # for now
    
    nyc_locations = get_coordinates(distance, focus_coordinates)
    
    st.session_state['map'].data = nyc_locations
    
    st.session_state['header'].body = f'Locations within {distance:.0f}m of location X'
    

if 'map' not in st.session_state:
    # init
    st.session_state['map'] = 'value'
else:
    # update
    update_app()


   
    
