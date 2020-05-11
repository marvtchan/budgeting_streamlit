# streamlit_example.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
import os
import datetime as dt
from datetime import datetime
from datetime import timedelta
import dateutil.relativedelta
import seaborn as sns
import matplotlib.pyplot as plt

engine = create_engine('sqlite:////Users/marvinchan/Documents/PythonProgramming/DatabaseforStatements/BudgetingProject/transactions_ledger.db', echo=False)
connection = engine.raw_connection()

def main():
    data = load_data()
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Analysis"])

    if page == "Homepage":
        st.title("💸Budgeting Analysis💸")
        st.markdown(
        """
        This is an exploratory analysis for personal finances.
        [See source code](https://github.com/marvtchan/BudgetingProject)

        The data presented are transactions from 2019-01-01 to the current month.

        Each transaction is categorized with an SVM model and uploaded to a SQLite database. 

        Every month the categorization and upload is set to rerun for up-to-date data.

        Transactions are split into the following categories:

            Income
            Rent
            Food 
            Shopping 
            Gas 
            Travel 
            Cash 
            Pet 
            Gifts 
            Gym 
            Transfer 
            Groceries 
            Bills 
            Uncategorized 
            Entertainment 
            Credit Card Reward 
        """)
        st.subheader("Analysis")
        st.markdown(
        """
        Under the analysis page there will be a bar chart with customizable date ranges and category variables. 

        The data is explored with a seaborn bar chart.
        """)
    elif page == "Analysis":
        st.title("📈Analysis📉")
        st.markdown(
        """
        The analysis below shows a bar chart of monthly transaction data aggregated by categories.

        To analyze:

           1. Navigate to sidebar for options.

           2. Select date range and categories for monthly analysis. 

           3. Check filtered data and raw data for deeper insight.

           4. Expense is negative while income is positive.

        """)
        start_date, end_date = get_dates()
        selected_filtered_data, categories, filtered = filter_data(data, start_date, end_date)
        get_chart(selected_filtered_data, start_date, end_date, categories, filtered)



@st.cache(persist=True)
def load_data():
    engine = create_engine('sqlite:////Users/marvinchan/Documents/PythonProgramming/DatabaseforStatements/BudgetingProject/transactions_ledger.db', echo=False)
    connection = engine.raw_connection()
    data = pd.read_sql_query('SELECT * FROM transactions_categorized_aggregate', connection)
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
    data = data.sort_values(by=['Date'])
    return data

def get_dates():
    start_str = "2019-01-01"
    start = datetime.strptime(start_str, '%Y-%m-%d')
    today = datetime.today()
    first = today.replace(day=1)
    end = first - dt.timedelta(days=1)
    start_date = st.sidebar.date_input('Start date', start)
    end_date = st.sidebar.date_input('End date', end)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')
    return start_date, end_date    

def filter_data(data, start_date, end_date):
    filtered = data[
    (data['Date'] >= start_date) & (data['Date'].dt.date <= (end_date))
    ]
    categories  = st.sidebar.multiselect("Enter categories", filtered['Category'].unique())
    selected_filtered_data = filtered[(filtered['Category'].isin(categories))]
    return selected_filtered_data, categories, filtered


def get_chart(selected_filtered_data, start_date, end_date, categories, filtered):
    try:
        ax = sns.barplot(y ="Amount", data=selected_filtered_data, palette="GnBu_d", x='Month', ci=None, estimator=sum)
        plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='small')
        plt.xlabel('Month',fontsize=12)
        st.subheader("Monthly Expenses by Categories")
        st.pyplot()
        st.success('Category: `%s`' % (categories))
    except ValueError:
        st.error('Select Categories for bar chart.')

    categorical_data_is_check = st.checkbox("Display the data of selected categories")
    if categorical_data_is_check:
        st.subheader("Filtered data by date between '%s' and '%s' for '%s" % (start_date, end_date, categories))
        st.write(selected_filtered_data)

    if st.checkbox("Display total data", False):
        st.subheader("Raw data by date between '%s' and '%s'" % (start_date, end_date))
        st.write(filtered)

if __name__ == "__main__":
    main()
