import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Twitter Data Analysis"
)

# st.sidebar.success("Select a page above.")
st.header("Our final Cleaned dataset for Users with Classification:")
df = pd.read_csv('Final_Users_File.csv')
st.dataframe(df)

st.header("Count of different user groups present in our dataset")

bar = df["user_category"].value_counts().rename_axis('user_categories').reset_index(name='counts')
fig = px.bar(bar, x='user_categories', y='counts', color_discrete_sequence=px.colors.sequential.Viridis)
st.plotly_chart(fig)

st.header("Top 15 countries present in our dataset")
bar1 = df["location_country"].value_counts().rename_axis('location').reset_index(name='counts')
s = bar1.head(15)
fig1 = px.bar(s, y='location', x='counts', color_discrete_sequence=px.colors.sequential.Viridis)

fig1.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig1)
