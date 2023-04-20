import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.express as px
import numpy as np
import plotly
import os

# Initial Setup
st.set_page_config(
    page_title="Twitter Data Analysis", page_icon=":bar_chart:", layout="wide"
)


def read_file(output_files_dir, filename):
    return pd.read_csv(os.path.join(output_files_dir, filename))


_output_files_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Final Output Files",
)

df = read_file(_output_files_dir, "Final_Users_File.csv")

dataframe = read_file(_output_files_dir, "Final_Tweet_Data.csv")

st.sidebar.header("Please Filter Here:")
country = st.sidebar.multiselect(
    "Select the Country:", options=df["location_country"].unique(), default="Germany"
)
city = st.sidebar.multiselect(
    "Select the City:", options=df["location_city"].unique(), default="Magdeburg"
)
state = st.sidebar.multiselect(
    "Select the State:", options=df["location_state"].unique(), default="Saxony-Anhalt"
)

category = st.sidebar.multiselect(
    "Select the Category:",
    options=df["user_category"].unique(),
    default=df["user_category"].unique(),
)

df_selection = df.query("location_country == @country & user_category == @category ")

dataframe_selection = dataframe.query(
    "location_country == @country & user_category == @category "
)

df_selection1 = df.query("location_city == @city ")

df_selection2 = df.query("location_state == @state ")

st.title(":bar_chart: Twitter Data Dashboard")
st.markdown("___")

total_users = df_selection["username"].count()
user_categories = df_selection["user_category"].nunique()

left_column, middle_column = st.columns(2)
with left_column:
    st.subheader("Total Users:")
    st.subheader(f"{total_users}")
with middle_column:
    st.subheader("Number of Categories:")
    st.subheader(f"{user_categories}")

st.markdown("___")

# Plotting Graph
df_selectiona = (
    df_selection["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
category_labelsa = df_selectiona.user_categories
category_valuesa = df_selectiona.counts

fig = px.pie(
    df_selectiona,
    values=category_valuesa,
    names=category_labelsa,
    title=" Different User Groups Present ",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
st.plotly_chart(fig)

df_selection1b = (
    df_selection1["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
category_labelsb = df_selection1b.user_categories
category_valuesb = df_selection1b.counts

fig1 = px.pie(
    df_selection1b,
    values=category_valuesb,
    names=category_labelsb,
    title=" Different User Groups Present based on City ",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
st.plotly_chart(fig1)

df_selection2c = (
    df_selection2["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
category_labelsc = df_selection2c.user_categories
category_valuesc = df_selection2c.counts

fig2 = px.pie(
    df_selection2c,
    values=category_valuesc,
    names=category_labelsc,
    title=f" Different User Groups present in {state} state ",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
st.plotly_chart(fig2)

datafra_selectiona = (
    dataframe_selection["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
category_labelsad = datafra_selectiona.user_categories
category_valuesad = datafra_selectiona.counts

fig = px.pie(df_selectiona,
             values=category_valuesad,
             names=category_labelsad,
             title=" Percentage of tweets by user groups ",
             color_discrete_sequence=px.colors.sequential.Viridis
             )
st.plotly_chart(fig)

final1 = (
    dataframe["location_country"]
    .value_counts()
    .rename_axis("Countries")
    .reset_index(name="counts")
)

final0 = final1[
    (final1["Countries"] != "Germany") & (final1["Countries"] != "Unknown")
]["counts"].sum()

Others = [["Others", final0]]
otherdf = pd.DataFrame(Others, columns=["Countries", "counts"])
final1 = final1.append(otherdf)

n1 = final1[
    (final1["Countries"] == "Germany")
    | (final1["Countries"] == "Unknown")
    | (final1["Countries"] == "Others")
]
category_lab = n1.Countries
category_val = n1.counts

fig = px.pie(
    n1,
    values=category_val,
    names=category_lab,
    title="Percentage of Tweets",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
st.plotly_chart(fig)
