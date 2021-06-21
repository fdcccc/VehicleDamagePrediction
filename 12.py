
import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.express as px



# In[ ]:streamlit run 12.py

st.title('Price Chart')
id = st.sidebar.text_input("Enter Stock Ticke (example: AAPL)")
stock = yf.Ticker(id)
df=stock.history(period='max')['Close']
if len(df)==0:
    st.write('Invalid Stock Ticker')
else:
    df.index=pd.DatetimeIndex(df.index)
    year= st.sidebar.selectbox('Year', tuple(sorted(set(df.index.year))) )
    
    month= st.sidebar.selectbox("Month", tuple(sorted(set(df[df.index.year==year].index.month))) )



    try:
        year=int(year)
        month=int(month)
        df2=df[(pd.DatetimeIndex(df.index).year==year) & (pd.DatetimeIndex(df.index).month==month) ].reset_index()
        df2.columns=['Date','Price']

        st.write(px.line(df2, x='Date', y='Price', title=str(id)+" "+ str(year) +"-"+str(month)))
    except:
        pass
    
