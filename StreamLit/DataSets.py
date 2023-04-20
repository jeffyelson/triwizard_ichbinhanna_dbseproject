import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Initial Setup
st.set_page_config(
    page_title="Twitter Data Analysis", page_icon=":bar_chart:", layout="wide"
)

st.title("Overall Extracted Dataset")
st.markdown("___")


def read_file(output_files_dir, filename):
    return pd.read_csv(os.path.join(output_files_dir, filename))


_output_files_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Final Output Files"
)

df_users = read_file(_output_files_dir, "Final_Users_File.csv")
df_tweets = read_file(_output_files_dir, "Final_Tweet_Data.csv")

pie_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=50, r=0, b=0, t=0, pad=0),
    font=dict(size=20),
    legend=dict(font=dict(size=20)),
)

hist_layout = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=100, r=0, b=50, t=0, pad=0),
    font=dict(size=20),
    legend=dict(font=dict(size=20)),
)

# st.sidebar.success("Select a page above.")
st.header("Our final Cleaned dataset for Users with Classification:")

st.dataframe(df_users)

st.header("Count of different user groups present in our dataset")

bar = (
    df_users["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
fig = px.bar(
    bar,
    x="user_categories",
    y="counts",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
fig.update_layout(pie_layout)
st.plotly_chart(fig)

st.header("User groups present in our dataset")
pie = (
    df_users["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
fig = px.pie(
    pie,
    names="user_categories",
    values="counts",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
fig.update_layout(pie_layout)
st.plotly_chart(fig)
# fig.write_image("pie_user_groups.png", scale=6, width=500, height=500)

st.header("Tweets by User groups present in our dataset")
pie = (
    df_tweets["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
fig = px.pie(
    pie,
    names="user_categories",
    values="counts",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
fig.update_layout(pie_layout)
st.plotly_chart(fig)
# fig.write_image("pie_user_group_tweets.png", scale=6, width=500, height=500)

st.header("Tweets in different languages")


def update_languages(lang):
    if lang == "de":
        return "German"
    elif lang == "en":
        return "English"
    elif lang in ["qht", "qme", "qam", "qst"]:
        return "No Text"
    else:
        return "Others"


df_tweets["Languages"] = df_tweets["lang"].apply(lambda x: update_languages(x))
pie = (
    df_tweets["Languages"]
    .value_counts()
    .rename_axis("Languages")
    .reset_index(name="counts")
)
fig = px.pie(
    pie,
    names="Languages",
    values="counts",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
fig.update_layout(pie_layout)
st.plotly_chart(fig)
# fig.write_image("pie_languages.png", scale=6, width=500, height=500)


def get_quarter(created_at):
    temp = created_at.split()[0].split("-")

    if temp[1] in ["01", "02", "03"]:
        quarter = "Q1"
    elif temp[1] in ["04", "05", "06"]:
        quarter = "Q2"
    elif temp[1] in ["07", "08", "09"]:
        quarter = "Q3"
    else:
        quarter = "Q4"

    return [temp[0], quarter]


bar = df_tweets[["idx", "created_at", "user_category"]]
bar[["Year", "Quarter"]] = bar.apply(
    lambda x: get_quarter(x["created_at"]), axis=1, result_type="expand"
)
agg_dict = {"idx": ["count"]}
bar["Concat"] = bar["Year"].astype(str) + " - " +  bar["Quarter"].astype(str)
bar = bar.groupby(["user_category", "Concat"], as_index=False).agg(agg_dict)
bar.columns = bar.columns.droplevel(1)
bar.rename(columns={"idx": "Count", "user_category": "User Category"}, inplace=True)
bar["Year"] = bar["Concat"].apply(lambda x: x.split(" - ")[0])
st.header("Tweets in different Quarters 2021 and 2022")
fig = px.histogram(
    bar[(bar["Year"] == "2021") | (bar["Year"] == "2022")],
    x="User Category",
    y="Count",
    barmode="group",
    color="Concat",
    color_discrete_sequence=px.colors.sequential.Viridis,
    range_y=[0, 4000],
)
fig.update_layout(hist_layout)
st.plotly_chart(fig)
# fig.write_image("saved_images/time_graph_2021.png", scale=6, width=2000, height=500)
# st.header("Tweets in different Quarters 2022")
# fig = px.histogram(
#     bar[bar["Year"] == "2022"],
#     x="User Category",
#     y="Count",
#     barmode="group",
#     color="Quarter",
#     color_discrete_sequence=px.colors.sequential.Viridis,
#     range_y=[0, 4000],
# )
# fig.update_layout(hist_layout)
# st.plotly_chart(fig)
# fig.write_image("time_graph_2022.png", scale=6, width=1000, height=500)


st.header("User groups present in our dataset")
pie = (
    df_users["user_category"]
    .value_counts()
    .rename_axis("user_categories")
    .reset_index(name="counts")
)
fig = px.pie(
    pie,
    names="user_categories",
    values="counts",
    color_discrete_sequence=px.colors.sequential.Viridis,
)
st.plotly_chart(fig)

st.header("Top 15 countries present in our dataset")
bar1 = (
    df_users["location_country"]
    .value_counts()
    .rename_axis("location")
    .reset_index(name="counts")
)
s = bar1.head(15)
fig1 = px.bar(
    s, y="location", x="counts", color_discrete_sequence=px.colors.sequential.Viridis
)

fig1.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig1)
