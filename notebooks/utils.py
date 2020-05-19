import pandas as pd 
from typing import List
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os

# ##### #
# Regex #
# ##### #

#Fonte: https://github.com/nathanshartmann/portuguese_word_embeddings
punctuations = re.escape('!"#%\'()*+,./:;<=>?@[\\]^_`{|}~')
re_remove_brackets = re.compile(r'\{.*\}')
re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
re_transform_numbers = re.compile(r'\d', re.UNICODE)
re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)
# Different quotes are used.
re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
re_tree_dots = re.compile(u'…', re.UNICODE)
# Differents punctuation patterns are used.
re_punkts = re.compile(r'(\w+)([%s])([ %s])' % (punctuations, punctuations), re.UNICODE)
re_punkts_b = re.compile(r'([ %s])([%s])(\w+)' % (punctuations, punctuations), re.UNICODE)
re_punkts_c = re.compile(r'(\w+)([%s])$' % (punctuations), re.UNICODE)
re_changehyphen = re.compile(u'–')
re_doublequotes_1 = re.compile(r'(\"\")')
re_doublequotes_2 = re.compile(r'(\'\')')
re_trim = re.compile(r' +', re.UNICODE)
re_remove_pic = re.compile(r"pic.twitter.com\S+")

def clean_text(text: str):
    """Apply all regex above to a given string."""
    text = text.lower()
    text = re_tree_dots.sub('...', text)
    text = re.sub('\.\.\.', '', text)
    text = re_remove_brackets.sub('', text)
    text = re_changehyphen.sub('-', text)
    text = re_remove_html.sub(' ', text)
    text = re_transform_numbers.sub('0', text)
    text = re_transform_url.sub('', text)
    text = re_transform_emails.sub('EMAIL', text)
    text = re_quotes_1.sub(r'\1"', text)
    text = re_quotes_2.sub(r'"\1', text)
    text = re_quotes_3.sub('"', text)
    text = re.sub('"', '', text)
    text = re_dots.sub('.', text)
    text = re_punctuation.sub(r'\1', text)
    text = re_hiphen.sub(' - ', text)
    text = re_punkts.sub(r'\1 \2 \3', text)
    text = re_punkts_b.sub(r'\1 \2 \3', text)
    text = re_punkts_c.sub(r'\1 \2', text)
    text = re_doublequotes_1.sub('\"', text)
    text = re_doublequotes_2.sub('\'', text)
    text = re_trim.sub(' ', text)
    text = re_remove_pic.sub("", text)
    return text.strip()

def get_hashtags(df: pd.DataFrame) -> List[str]:
    "Função para extrair hashtags de uma coluna com strings no formato: '['hashtag1', 'hashtag2']' "

    all_hashtags = []
    for i in range(len(df)):
        raw = df["hashtags"].iloc[i][1:-1]
        if len(raw)  == 0: continue
        hashtags = [tag_to_clean.strip()[1:-1] for tag_to_clean in raw.split(",")]
        
        all_hashtags.extend(hashtags)
    
    return all_hashtags

def build_wordcloud(text_list: List[str], output_file: str = "wordcloud.png", save_file: bool = False) -> None:
    "Função encarregada de gerar WordClouds"
    # Limpeza dos tweets
    text_list = [clean_text(text) for text in text_list]
    stop_words = stopwords.words("portuguese")
    wc = WordCloud(colormap='binary', max_words=200, stopwords=stop_words, background_color='white', width=1600, height=800)
    cloud = wc.generate(' '.join(text_list))
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis("off")
    # plt.close()

    if save_file: wc.to_file(output_file)

def get_tweets_from_folder(path: str) -> pd.DataFrame:

    tweet_df = pd.DataFrame()

    for day in os.listdir(path):
        current_df = pd.read_csv(os.path.join(path, day))
        tweet_df = tweet_df.append(current_df, ignore_index=True)
    
    return tweet_df

def get_tweets_by_day(df: pd.DataFrame, normalize: bool = False) -> pd.DataFrame:

    tweets_by_day_df = pd.DataFrame(columns=["data", "positivos", "neutros", "negativos", "hashtags"])

    for day in df["date"].unique():
        day_df = {}
        current_day_df = df[df["date"] == day]
        day_df["data"] = day
        day_df["positivos"] = (current_day_df["sentiment"] == "Positivo").sum()
        day_df["neutros"] = (current_day_df["sentiment"] == "Neutro").sum()
        day_df["negativos"] = (current_day_df["sentiment"] == "Negativo").sum()
        day_df["total"] = len(current_day_df)
        day_df["hashtags"] = get_hashtags(current_day_df)
        print()

        tweets_by_day_df = tweets_by_day_df.append(day_df, ignore_index=True)
    
    if normalize:
        tweets_by_day_df["positivos"] /= tweets_by_day_df["total"]
        tweets_by_day_df["neutros"] /= tweets_by_day_df["total"]
        tweets_by_day_df["negativos"] /= tweets_by_day_df["total"]

    return tweets_by_day_df

def contabilize_hashtags(hashtags: List[str]) -> pd.DataFrame:

    hashtags_df = pd.DataFrame(hashtags, columns=["hashtag"])
    hashtag_count = {}

    for hashtag in hashtags_df["hashtag"].unique().tolist():
        hashtag_count[hashtag] = (hashtags_df["hashtag"] == hashtag).sum()
    
    unique_hashtags_df = pd.DataFrame(hashtag_count.values(), index=hashtag_count.keys(), columns=["quantidade"])
    unique_hashtags_df.sort_values("quantidade", ascending=False, inplace=True)

    return unique_hashtags_df


