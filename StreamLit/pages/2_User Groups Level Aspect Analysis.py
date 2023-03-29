import streamlit as st
import pandas as pd
import os
from wordcloud import WordCloud
from wordcloud import get_single_color_func
import matplotlib.pyplot as plt
import math

# Initial Setup
st.set_page_config(page_title="User Category Level Aspect Analysis",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

st.sidebar.header("Please Filter Here:")

st.title("User Category Level Aspect Analysis")
st.markdown("___")


def read_aspects_file(output_files_dir, filename):
    return pd.read_csv(os.path.join(output_files_dir, filename))


def read_co_occurence_file(output_files_dir, filename):
    return pd.read_csv(os.path.join(output_files_dir, filename))


_output_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                 'Final Output Files')

st.set_option('deprecation.showPyplotGlobalUse', False)

output_files = {"PyABSA": "PyABSA_FinalOutputWithCategory.csv", "Approach 1": "Approch1_FinalOutputWithCategory.csv",
                "Approach 2": "Approch2_FinalOutputWithCategory.csv"}
aspect_file = "Final_Co-occuring_Aspects.csv"

output_file = st.sidebar.selectbox(
    "Select the Output File:",
    options=output_files.keys()
)

_df = read_aspects_file(_output_files_dir, output_files[output_file])
_df_co_aspects = read_co_occurence_file(_output_files_dir, aspect_file)

_category = st.sidebar.multiselect(
    "Select the Category:",
    options=_df['Category'].unique(),
    default=_df['Category'].unique()[0]
)

aspect_levels_list = ["Individual Aspect", "Aspect Category"]

selected_level = st.sidebar.selectbox(
    "Select Analysis Level:",
    options=aspect_levels_list
)

if selected_level == aspect_levels_list[0]:
    table_level = "Aspect"
else:
    table_level = "Aspect_Category"


# Custom Wordcloud functions

def get_color_wc(row):
    if (row["Negative"] >= row["Positive"]) and (row["Negative"] >= row["Neutral"]):
        percent = row["Negative"] / row["Count"]
        r_value = 255 - int(percent * 100)
        g_value = 0
        b_value = 0
    elif (row["Positive"] >= row["Negative"]) and (row["Positive"] >= row["Neutral"]):
        percent = row["Positive"] / row["Count"]
        r_value = 0
        g_value = 255 - int(percent * 100)
        b_value = 0
    else:
        percent = row["Neutral"] / row["Count"]
        r_value = 255 - int(percent * 100)
        g_value = 255 - int(percent * 100)
        b_value = 255 - int(percent * 100)

    #     if (row["Negative"] >= row["Positive"]):
    #         percent = row["Negative"]/row["Count"]
    #         r_value = int(percent * 255)
    #         g_value = 0
    #     else:
    #         percent = row["Positive"]/row["Count"]
    #         r_value = 0
    #         g_value = int(percent * 255)

    return '#%02x%02x%02x' % (r_value, g_value, b_value)


def get_color_dict_wc(color_col, cat_col):
    color_dict = {}

    for i in range(len(color_col)):
        if color_col[i] in color_dict.keys():
            color_dict[color_col[i]].append(cat_col[i])
        else:
            color_dict[color_col[i]] = [cat_col[i]]

    return color_dict


def get_count_dict(cat_col, count_col):
    count_dict = {}

    for i in range(len(cat_col)):
        count_dict[cat_col[i]] = count_col[i]

    return count_dict


class GroupedColorFunc(object):

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (get_single_color_func(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = get_single_color_func(default_color)

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)(word, **kwargs)


def generate_word_cloud_for_category(df, category, wordcloud_category, _wordcloud):
    agg_dict = {"Count": ["sum"], "Negative": ["sum"], "Neutral": ["sum"], "Positive": ["sum"]}
    df = df.groupby(by=["Category", wordcloud_category]).agg(agg_dict).reset_index()
    df.columns = df.columns.droplevel(1)
    df["Count"] = df["Count"].astype(int)
    df["Color"] = df.apply(lambda x: get_color_wc(x), axis=1)

    nrows = math.ceil(len(category) / 2)
    ncols = 2

    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 12))
    axes = axes.flatten()

    for i in range(len(axes)):

        if i >= len(category):
            fig.delaxes(axes[i])
            break

        # Setup data, assign colors to categories and extract count
        temp = df[df["Category"] == category[i]]
        color_dict = get_color_dict_wc(temp["Color"].to_list(), temp[wordcloud_category].to_list())
        count_dict = get_count_dict(temp[wordcloud_category].to_list(), temp["Count"].to_list())

        # Generate wordcloud
        _wordcloud.generate_from_frequencies(frequencies=count_dict)
        default_color = 'grey'

        # Create a color function with multiple tones
        grouped_color_func = GroupedColorFunc(color_dict, default_color)

        # Apply our color function
        _wordcloud.recolor(color_func=grouped_color_func)

        # Set Header
        v = 'WordCloud for {} '.format(category[i])
        axes[i].set_title(v)

        # Plot
        #         plt.figure()
        axes[i].imshow(_wordcloud, interpolation="bilinear")
        axes[i].axis("off")
        axes[i].plot()

    st.pyplot(fig)
    # plt.savefig("Wordcloud.png", bbox_inches='tight')


# Custom table functions

def get_sentiment(row):
    if (row["Negative"] >= row["Positive"]) and (row["Negative"] >= row["Neutral"]):
        return "Negative"
    elif (row["Positive"] >= row["Negative"]) and (row["Positive"] >= row["Neutral"]):
        return "Positive"
    else:
        return "Neutral"


def get_color_tb(row):
    color_if_neg = '#F2543D'
    color_if_neu = '#EEEEEE'
    color_if_pos = '#38C477'

    return_list = []

    num = int(len(row) / 2)

    for i, v in enumerate(row):
        if i < num and (row.iloc[num + i] == "Negative"):
            return_list.append('background-color: {}'.format(color_if_neg))
        elif i < num and (row.iloc[num + i] == "Neutral"):
            # return_list.append('background-color: {}'.format(color_if_neu))
            return_list.append("")
        elif i < num and (row.iloc[num + i] == "Positive"):
            return_list.append('background-color: {}'.format(color_if_pos))
        else:
            return_list.append("")

    return return_list


def get_color_dict_tb(aspects):
    kelly_colors_hex = ["#FFB300", "#803E75", "#FF6800", "#A6BDD7", "#C10020",
                        "#CEA262", "#817066", "#007D34", "#F6768E", "#00538A",
                        "#FF7A5C", "#53377A", "#FF8E00", "#B32851", "#F4C800",
                        "#7F180D", "#93AA00", "#593315", "#F13A13",
                        "#232C16"]

    color_dict = {}
    i = 0

    for aspect in aspects:
        color_dict[aspect] = kelly_colors_hex[i % len(kelly_colors_hex)]
        i += 1

    return color_dict


def get_aspect_color(row, color_dict):
    return_list = []

    for i, v in enumerate(row):
        return_list.append('background-color: {}'.format(color_dict[v]))

    return return_list


def create_table(df_absa, level, category_list):
    agg_dict = {"Count": ["sum"], "Negative": ["sum"], "Neutral": ["sum"], "Positive": ["sum"]}
    df_absa = df_absa.groupby(by=["Category", level]).agg(agg_dict).reset_index()
    df_absa.columns = df_absa.columns.droplevel(1)
    df_absa = df_absa.sort_values("Count", ascending=False)
    df_absa["Sentiment"] = df_absa.apply(lambda x: get_sentiment(x), axis=1)

    aspect_list = []

    if len(category_list) >= 1:
        for i in range(len(category_list)):
            if i == 0:
                df_category_aspect = df_absa[df_absa["Category"] == category_list[i]][[level, "Sentiment"]].reset_index(
                    drop=True).head(15)
                df_category_aspect.rename(
                    columns={level: category_list[i] + "_" + level, "Sentiment": category_list[i] + "_Sentiment"},
                    inplace=True)
                aspect_list += df_category_aspect[category_list[i] + "_" + level].to_list()
            else:
                temp = df_absa[df_absa["Category"] == category_list[i]][[level, "Sentiment"]].reset_index(
                    drop=True).head(15)
                temp.rename(
                    columns={level: category_list[i] + "_" + level, "Sentiment": category_list[i] + "_Sentiment"},
                    inplace=True)
                aspect_list += temp[category_list[i] + "_" + level].to_list()
                df_category_aspect = df_category_aspect.merge(temp, left_index=True, right_index=True)

        keep_cols = []
        drop_cols = []
        cols = df_category_aspect.columns

        for col in cols:
            if "Sentiment" in col:
                drop_cols.append(col)
            else:
                keep_cols.append(col)

        df_ranks = df_category_aspect[keep_cols]
        df_category_aspect = df_category_aspect[keep_cols + drop_cols]

        styled_df1 = df_category_aspect.style.apply(lambda x: get_color_tb(x), axis=1)

        color_dict = get_color_dict_tb(aspect_list)

        styled_df2 = df_ranks.style.apply(lambda x: get_aspect_color(x, color_dict), axis=1)

        return styled_df1, styled_df2
    else:
        return None, None


# Co-occuring aspects
def generate_bar_graphs(df, category):
    agg_dict = {"Count": ["sum"]}
    df = df.groupby(["Category", "Aspects"]).agg(agg_dict).reset_index()
    df.columns = df.columns.droplevel(1)
    df = df.sort_values("Count", ascending=False)

    #     nrows = math.ceil(len(category) / 2)
    #     ncols = 2

    #     fig, axes = plt.subplots(nrows, ncols)
    #     fig.tight_layout()

    fig, axes = plt.subplots(len(category), 1, figsize=(6, 10), sharex=True)
    if len(category) == 1:
        axes = [axes]

    plt.xlim(0, 100)
    fig.tight_layout()

    #     if len(category) >= 1:
    #         axes = axes.flatten()

    for i in range(len(category)):
        #         if i >= len(category):
        #             fig.delaxes(axes[i])
        #             break

        # Setup data, assign colors to categories and extract count
        temp = df[df["Category"] == category[i]].head(5)
        if len(temp) <= 0:
            fig.delaxes(axes[i])
            continue

        # Set Header
        v = '{} for {} '.format("Aspects", category[i])
        axes[i].set_title(v)

        aspects = temp["Aspects"]
        aspect_counts = temp["Count"]

        axes[i].barh(aspects, aspect_counts, align='center', color="steelblue")
        axes[i].invert_yaxis()
        axes[i].set_xlabel("Count")
        axes[i].tick_params(axis='both', which='both', labelbottom=True)

    plt.subplots_adjust(hspace=0.4)
    st.pyplot(fig)


# Execution
# Table Generation
st.header("Top " + table_level + " in different user groups")
final_table1, final_table2 = create_table(_df, table_level, _category)

if final_table1 is not None:
    st.dataframe(final_table1)
    # st.dataframe(final_table2)

# Co-occuring Aspects
st.header("Top Co-occuring aspects in user groups")
if len(_category) > 0:
    generate_bar_graphs(_df_co_aspects, _category)

# Wordcloud Generation
wc = WordCloud(background_color='white', width=500, height=500, collocations=False)

st.header("Wordclouds for " + table_level + " in different user groups")
if len(_category) > 0:
    generate_word_cloud_for_category(_df, _category, table_level, wc)
# st.dataframe(df['Sentiment'])
