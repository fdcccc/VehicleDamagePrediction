import streamlit as st

import pandas as pd
import numpy as np
import dill
import geopandas as gpd

import json
import bokeh.io


from bokeh.io import show
from bokeh.models import GeoJSONDataSource,ColumnDataSource,LogColorMapper,ColorBar,LinearColorMapper
from bokeh.plotting import figure
from bokeh.sampledata.sample_geojson import geojson
from bokeh.palettes import Blues8  as palette
from bokeh.models import HoverTool



# In[8]:


model_crime=dill.load(open('model_crime.pkd','rb'))
model_crash=dill.load(open('model_crash.pkd','rb'))
current=dill.load(open('current.pkd', 'rb'))
model_all_crime=dill.load(open('model_all_crime.pkd','rb'))
model_all_crash=dill.load(open('model_all_crash.pkd','rb'))
current_all=dill.load(open('current_all.pkd', 'rb'))
his=dill.load(open('history.pkd','rb'))

with st.sidebar:  
    st.write("## Select month and days of the week to see the prediciton in the next 6 months.")
    Month_sel=st.selectbox("Month", ('2021-08','2021-09','2021-10','2021-11','2021-12','2022-01') )
    dw=st.selectbox("Days of the Week", ('Weekdays','Weekends','Everyday')) 
    st.text("")
    st.text("")

    st.info("The prediction can be shown by incident numbers or incident rates (per 10,000 population)")
    st.write("## Select prediction type")
    im=st.radio('',['Numbers' , 'Rates'])
    
