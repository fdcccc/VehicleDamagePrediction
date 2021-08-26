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
    
dwl={'Weekdays':'weekday','Weekends':'weekend','Everyday':'all'}
day_of_week_pre=dwl[dw]
Year_pre,Month_pre=int(Month_sel.split('-')[0]),int(Month_sel.split('-')[1])

if Year_pre==2021:
    k=Month_pre-7
if Year_pre==2022:
    k=Month_pre+5

if day_of_week_pre !='all':    
    current['pre']['Year']=Year_pre
    current['pre']['Month']=Month_pre
    current['pre']['day_of_week']=day_of_week_pre

    crime_pre=current['pre'].copy()
    crime_pre['mean-'+str(k)]=current['crime'][(current['crime'])['day_of_week']==day_of_week_pre]['mean'].values
    crime_pre['Total']=model_crime[k].predict(crime_pre).round(2)
    crash_pre=current['pre'].copy()
    crash_pre['mean-'+str(k)]=current['crash'][(current['crash'])['day_of_week']==day_of_week_pre]['mean'].values
    crash_pre['Total']=model_crash[k].predict(crash_pre).round(2)
    total_pre=current['pre'].copy()
    total_pre['Total']=crime_pre['Total']+crash_pre['Total']
    total_pre['Rate']=(total_pre['Total']/total_pre['TOT_POP']*10000).round(2)
    
if day_of_week_pre =='all':    
    current_all['pre']['Year']=Year_pre
    current_all['pre']['Month']=Month_pre
    crime_pre=current_all['pre'].copy()
    crime_pre['mean-'+str(k)]=current_all['crime']['mean'].values
    crime_pre['Total']=model_all_crime[k].predict(crime_pre).round(2)
    crash_pre=current_all['pre'].copy()
    crash_pre['mean-'+str(k)]=current_all['crash']['mean'].values
    crash_pre['Total']=model_all_crash[k].predict(crash_pre).round(2)
    total_pre=current_all['pre'].copy()
    total_pre['Total']=crime_pre['Total']+crash_pre['Total']
    total_pre['Rate']=(total_pre['Total']/total_pre['TOT_POP']*10000).round(2)



pal=list(palette)
pal.reverse()

area = gpd.read_file('geo.shp')
area=area.astype({'area_num_1': 'int'})
area=area.merge(total_pre,left_on='area_num_1',right_on='COMMUNITY')
geo_source = GeoJSONDataSource(geojson=area.to_json())



st.title('Vehicle Damage Prediction in Chicago Community Areas')


st.markdown('Vehicle damages can be accident related or crime related. Most common auto insurance claims include car crash, vandalism and theft. Auto insurance companies are interested in estimating the probability of vehicle damages.')


st.markdown('Many auto insurance companies promote their mobile Apps that can track driving patterns and frequently visited areas. This project aims to predict **car damages caused by crashes and crimes** in all community areas of Chicago in the next **6 months**, which is the usual auto insurance policy period.')

st.markdown('The data source is [Chicago Data Portal](https://data.cityofchicago.org/). Crime data is collected from 2010-01 to 2021-07, crash data is collected from 2017-09 to 2021-07.')

st.markdown("""---""")

if im=='Numbers':
    st.header('Prediction of car damage incident numbers.')
    p = figure(title='Car Damage Incidents Number Prediction for {t} ({wd})'.format(t=Month_sel,wd=dw.lower()),
               plot_width=700,plot_height=700)
    high=total_pre['Total'].max()
    high-=high%-10
    color_mapper = LinearColorMapper(palette=pal,low=0,high=high)
    p.patches('xs', 'ys', fill_color={'field': 'Total', 'transform': color_mapper}, 
              line_color='black', line_width=0.5, source=geo_source)
    p.title.text_font_size = '13pt'
    p.grid.grid_line_color = None
    p.axis.visible = False
    color_bar = ColorBar(color_mapper=color_mapper)                  
    p.add_layout(color_bar, 'right')
    hover1 = HoverTool()
    hover1.tooltips = [('Community','@community'),('Number', '@Total{0.00}')]
    p.add_tools(hover1)




    st.bokeh_chart(p)
    
if im=='Rates':
    st.header('Prediction of car damage incident rates (per 10,000 population).')
    p2 = figure(title='Car Damage Incidents Rate Prediction for {t} ({wd})'.format(t=Month_sel,wd=dw.lower()),
                plot_width=700, plot_height=700)
    high2=total_pre['Rate'].max()
    high2-=high2%(-10)
    color_mapper2 = LinearColorMapper(palette=pal,low=0,high=high2)
    geo_source = GeoJSONDataSource(geojson=area.to_json())
    p2.patches('xs', 'ys', fill_color={'field': 'Rate', 'transform': color_mapper2}, 
              line_color='black', line_width=0.5, source=geo_source)
    p2.title.text_font_size = '13pt'
    p2.grid.grid_line_color = None
    p2.axis.visible = False
    color_bar2 = ColorBar(color_mapper=color_mapper2)                  
    p2.add_layout(color_bar2, 'right')
    hover2 = HoverTool()
    hover2.tooltips = [('Community','@community'),('Rate', '@Rate{0.00}')]
    p2.add_tools(hover2)

    st.bokeh_chart(p2)

st.markdown("""---""")
st.header('Select community name to see historical data.')

comm = st.selectbox('',area['community'].sort_values()).title()
pl=his[his['GEOG']==comm]
pl['Time']=pd.to_datetime(pl['time'])


p3 = figure(title='Number of Monthly Car Damage Incidents in {c} from 2017-9 to 2021-7'.format(c=comm),
           width=700,height=500, x_axis_type="datetime")
p3.title.text_font_size = '12pt'

p3.line(x='Time', y='Total',line_width=2,source=ColumnDataSource(pl))

p3.xaxis.ticker.desired_num_ticks = 9
hover3 = HoverTool()
hover3.tooltips = [('Date','@time'),('Number', '@Total')]
p3.add_tools(hover3)


st.bokeh_chart(p3)
