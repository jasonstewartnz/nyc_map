import streamlit as st
import pandas as pd
import numpy as np
from snowflake import connector 

st.title( 'NYC Street Map' )

focus_coordinates = (-74.00296211242676,40.72143702499928)
distance = 2000

def get_coordinates():
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
            ST_X(primary_coordinate) as lng,
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
    my_cnx = connector.connect(**st.secrets["snowflake"])
    #     my_cur = my_cnx.cursor()

    # run a snowflake query and put it all in a var called my_catalog
    #     my_cur.execute(query_sql)
    #     nyc_locations = my_cur.fetchall()

    # put the dafta into a dataframe
    nyc_locations = pd.read_sql(query_sql, my_cnx)

    #     df = pd.DataFrame(
    #         np.random.randn(1000, 2) / [50, 50] + [40.72143702499928,-74.00296211242676],
    #         columns=['lat', 'lon'])
    
    st.map(nyc_locations)
    
    st.dataframe(nyc_locations['NAME','AMENITY','location','distance_away_m'])

get_coordinates()
