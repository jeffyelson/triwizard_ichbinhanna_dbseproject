import streamlit as st
from wordcloud import (WordCloud, get_single_color_func, STOPWORDS)
import pandas as pd
import matplotlib.pyplot as plt
import csv
import random

positive_words = []
negative_words = []

st.set_option('deprecation.showPyplotGlobalUse', False)
df = pd.read_csv('/Users/preetamnaik/PycharmProjects/IchBinHannaVisualisation/Approch2_FinalOutputWithCategory.csv')
df['Sentiment'] = (df['Positive'] - df['Negative']) / (df['Positive'] + df['Neutral'] + df['Negative'])

category = st.sidebar.selectbox(
    "Select the Category:",
    options=df['Category'].unique(),

)

df_selection = df.query(
    "Category == @category"
)
v = 'WordCloud for {} '.format(category)
st.header(v)


class GroupedColorFunc(object):
    """
    Uses different colors for different groups of words.
    """

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
        return self.get_color_func(word)(word, **kwargs)

    # Define functions to select a hue of colors arounf: grey, red and green


def red_color_func(word, font_size, position, orientation, random_state=None,
                   **kwargs):
    return "hsl(0, 100%%, %d%%)" % random.randint(30, 50)


def green_color_func(word, font_size, position, orientation, random_state=None,
                     **kwargs):
    return "hsl(100, 100%%, %d%%)" % random.randint(20, 40)


for column in df['Sentiment']:
    if column > 0:
        positive_words = df['Aspect_Category'].tolist()
    elif column < 0:
        negative_words = df['Aspect_Category'].tolist()

colors_words_dict = {
    'green': positive_words[:10],
    'red': negative_words
}
print(positive_words)

print('___________________')

print(negative_words)

df2 = pd.read_csv('/Users/preetamnaik/PycharmProjects/IchBinHannaVisualisation/Approch2_FinalOutputWithCategory.csv',
                  usecols=['Aspect_Category'])

cloud = WordCloud(background_color="white", max_words=50)

wordcloud1 = cloud.generate(' '.join(df2['Aspect_Category'].unique()))

grouped_color_func = GroupedColorFunc(colors_words_dict, 'white')
wordcloud1.recolor(color_func=grouped_color_func)

plt.figure()
plt.axis('off')
plt.imshow(wordcloud1, interpolation="bilinear")
plt.show()
st.pyplot()

st.dataframe(df['Sentiment'])
