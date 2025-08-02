from bs4 import BeautifulSoup
from urllib.parse import urlparse
from settings import *

with open("blacklist.txt") as f:
    domains = set(f.read().split("\n"))

def tracker_urls(row):
    soup = BeautifulSoup(row["html"])
    scripts = soup.find_all("script", {"src": True})
    srcs = [s.get("src") for s in scripts]

    links = soup.find_all("a", {"href": True})
    href = [l.get("href") for l in links]

    all_domains = [urlparse(s).hostname for s in srcs + href]
    return len([a for a in all_domains if a in domains])

def get_page_content(row):
    soup = BeautifulSoup(row["html"])
    text = soup.get_text()
    return text

# class Filter(self,results):
#     def __init__(self, results):
#         self.filtered = results.copy()
#         self.relevance_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#         self.sentiment_analyzer = SentimentIntensityAnalyzer()

#     def tracker_filter(self):
#         tracker_count = self.filtered.apply(tracker_urls, axis=1)
#         tracker_count[tracker_count > tracker_count.median()] = RESULT_COUNT
#         self.filtered["rank"] += tracker_count * 2

#     def content_filter(self):
#         page_content = self.filtered.apply(get_page_content, axis=1)
#         word_count = page_content.apply(lambda x: len(x.split(" ")))

#         word_count /= word_count.median()
#         word_count[word_count <= .5] = RESULT_COUNT
#         word_count[word_count != RESULT_COUNT] = 0
#         self.filtered["rank"] += word_count

#     def filter(self):
#         self.tracker_filter()
#         self.content_filter()
#         self.filtered = self.filtered.sort_values("rank", ascending=True)
#         self.filtered["rank"] = self.filtered["rank"].round()
#         return self.filtered

from transformers import pipeline
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Filter():
    def __init__(self, results):
        self.filtered = results.copy()
        self.relevance_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def nlp_relevance_score(self, query, text):
        result = self.relevance_model(sequences=text, candidate_labels=[query])
        score = result['scores'][0]  # Take the score for the relevant label
        return score
    
    def sentiment_score(self, text):
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        return sentiment['compound'] 
    
    def tracker_filter(self):
        tracker_count = self.filtered.apply(tracker_urls, axis=1)
        tracker_count[tracker_count > tracker_count.median()] = RESULT_COUNT
        self.filtered["rank"] += tracker_count * 2

    def content_filter(self, query):

        self.filtered['nlp_score'] = self.filtered.apply(lambda row: self.nlp_relevance_score(query, row['snippet']), axis=1)
        self.filtered['sentiment_score'] = self.filtered['snippet'].apply(self.sentiment_score)
        self.filtered['rank'] -= self.filtered['nlp_score'] * 10  # Adjust rank based on NLP score
        self.filtered['rank'] += self.filtered['sentiment_score'] * 5 

    def filter(self, query):
        self.tracker_filter()
        self.content_filter(query)
        self.filtered = self.filtered.sort_values("rank", ascending=True)
        self.filtered["rank"] = self.filtered["rank"].round()
        return self.filtered
