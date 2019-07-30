from django.core.management.base import BaseCommand
import os
import optparse
import numpy as np
import pandas as pd
import math
import json
import copy
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
tknzr = WordPunctTokenizer()
#nltk.download('stopwords')
stoplist = stopwords.words('english')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from mybook.models import BookData
from django.core.cache import cache
import sqlite3
import pandas as pd


#python manage.py load_data
class Command(BaseCommand):

    def handle(self, *args, **options):

        conn = sqlite3.connect('book.db')
        cur = conn.cursor()
        df = pd.read_sql("SELECT * FROM bookList", conn, index_col=None)
        conn.close()

        tot_textplots = df['keyword'].tolist()
        tot_titles = df['title'].tolist()
        tot_authors = df['author'].tolist()
        tot_genres = df['genre'].tolist()
        tot_infos = df['info'].tolist()

        nbooks = len(tot_titles[:])

        #delete all data
        BookData.objects.all().delete()

        for b in range(nbooks):
            bookdata = BookData()
            bookdata.title=tot_titles[b]
            bookdata.keyword=tot_textplots[b]
            bookdata.author=tot_authors[b]
            bookdata.genre=tot_genres[b]
            bookdata.info=tot_infos[b]

            bookdata.save()
