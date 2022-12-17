import streamlit as st
import pandas as pd
import numpy as np

st.title( 'NYC Street Map' )

focus_coordinates = (-74.00296211242676,40.72143702499928)
distance = 2000

def get_coordinates():
    sql = f"""
    SELECT *
    FROM OPENSTREETMAP_NEW_YORK.NEW_YORK.V_OSM_NY_AMENITY_SUSTENANCE
    WHERE ST_DWITHIN(ST_POINT({focus_coordinates[0]},{focus_coordinates[1]}),COORDINATES,{distance});
    """    
    
    # connect to snowflake
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    my_cur = my_cnx.cursor()

    # run a snowflake query and put it all in a var called my_catalog
    my_cur.execute("select color_or_style from catalog_for_website")
    my_catalog = my_cur.fetchall()

    # put the dafta into a dataframe
    sf_return_df = pandas.DataFrame(my_catalog)

    df = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [40.72143702499928,-74.00296211242676],
        columns=['lat', 'lon'])
    st.map(df)
    
    st.dataframe(sf_return_df)

get_coordinates()
