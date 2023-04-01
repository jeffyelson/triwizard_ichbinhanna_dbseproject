import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

# Initial Setup
st.set_page_config(page_title="User Category Level Aspect Analysis",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

st.sidebar.header("Please Filter Here:")

st.title("User Category Level Aspect Analysis")
st.markdown("___")


def read_file(output_files_dir, filename):
    return pd.read_csv(os.path.join(output_files_dir, filename))


_output_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'Final Output Files')

st.set_option('deprecation.showPyplotGlobalUse', False)

output_files = {"PyABSA": "PyABSA_FinalOutputWithCategory.csv", "Approach 1": "Approch1_FinalOutputWithCategory.csv",
                "Approach 2": "Approch2_FinalOutputWithCategory.csv"}

output_file = st.sidebar.selectbox(
    "Select the Output File:",
    options=output_files.keys()
)

_df = read_file(_output_files_dir, output_files[output_file])
_df_aspect_categories = read_file(_output_files_dir, "Final_Aspect_Categories.csv")

aspect_levels_list = ["Individual Aspect", "Aspect Category"]

selected_level = st.sidebar.selectbox(
    "Select Analysis Level:",
    options=aspect_levels_list
)

if selected_level == aspect_levels_list[0]:
    table_level = "Aspect"
else:
    table_level = "Aspect_Category"

aspect_list = _df[table_level].unique()
# aspect_list.sort()

_aspect = st.sidebar.multiselect(
    "Select " + table_level + ":",
    options=aspect_list,
    default=aspect_list[0]
)


# Custom functions
def generate_bar_graphs(df, level, aspect):
    agg_dict = {"Count": ["sum"], "Negative": ["sum"], "Neutral": ["sum"], "Positive": ["sum"]}
    df = df.groupby(["Category", level], as_index=False).agg(agg_dict)
    df.columns = df.columns.droplevel(1)

    fig, axes = plt.subplots(len(aspect), 1, figsize=(12, 12))

    if len(aspect) == 1:
        axes = [axes]

    for i in range(len(aspect)):
        # Setup data, assign colors to categories and extract count
        temp = df[df[level] == aspect[i]]
        x_axis = np.arange(len(temp))
        # temp.plot("Category", ["Negative", "Neutral", "Positive"], kind="bar", rot=0, color=["orangered", "khaki",
        # "green"])

        # Set Header
        #         v = '{} for {} '.format(graph_category, category[i])
        #         axes[i].set_title(v)

        axes[i].bar(x_axis - 0.3, temp["Negative"], width=0.2, label='Negative', color="firebrick")
        axes[i].bar(x_axis - 0.1, temp["Neutral"], width=0.2, label='Neutral', color="darkgrey")
        axes[i].bar(x_axis + 0.1, temp["Positive"], width=0.2, label='Positive', color="forestgreen")
        axes[i].legend()

        axes[i].set_xticks(x_axis, temp["Category"])
        axes[i].set_title(level + " - " + aspect[i])

    # plt.savefig("top-aspects.png", bbox_inches='tight', transparent=True)
    st.pyplot(fig)
    # plt.plot()


def create_category_table(df_cat, level, aspectList):
    df_cat = df_cat.sort_values("Frequency", ascending=False)

    if len(aspectList) >= 1:
        for i in range(len(aspectList)):
            if level == "Aspect":
                aspect_cat = df_cat[df_cat["Aspect"] == aspectList[i]]["Aspect_Category"].iloc[0]
            else:
                aspect_cat = aspectList[i]
            if i == 0:
                df_category_aspect = df_cat[df_cat["Aspect_Category"] == aspect_cat][
                    ["Aspect", "Frequency"]].reset_index(
                    drop=True).head(15)
                df_category_aspect.rename(
                    columns={"Aspect": aspect_cat, "Frequency": aspect_cat + "_Frequency"},
                    inplace=True)
                df_category_aspect[aspect_cat + "_Frequency"] = df_category_aspect[aspect_cat + "_Frequency"].astype(
                    str)
            else:
                temp = df_cat[df_cat["Aspect_Category"] == aspect_cat][["Aspect", "Frequency"]].reset_index(
                    drop=True).head(15)
                temp.rename(
                    columns={"Aspect": aspect_cat, "Frequency": aspect_cat + "_Frequency"},
                    inplace=True)
                temp[aspect_cat + "_Frequency"] = temp[aspect_cat + "_Frequency"].astype(str)
                df_category_aspect = df_category_aspect.merge(temp, left_index=True, right_index=True, how="outer")

        df_category_aspect = df_category_aspect.fillna("")

        styled_df = df_category_aspect.style.set_table_styles(
            [{"selector": "", "props": [("border", "1px solid grey")]},
             {"selector": "tbody td", "props": [("border", "1px solid grey")]},
             {"selector": "th", "props": [("border", "1px solid grey")]}
             ]
        )
        st.dataframe(styled_df)


if len(_aspect) >= 1:
    st.header("Aspect sentiments in different user groups")
    generate_bar_graphs(_df, table_level, _aspect)
    st.header("Aspect Categories")
    create_category_table(_df_aspect_categories, table_level, _aspect)
