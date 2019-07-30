from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import loader
from ast import literal_eval
import urllib
from mybook.models import BookData,UserProfile,ListBook
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.conf import settings
import logging
import json
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from django.core.cache import cache
import numpy as np
import unicodedata
import copy
import math
import nltk
from nltk.corpus import stopwords
from itertools import zip_longest
from collections import defaultdict
import pandas as pd

nbooksperquery=5

def home(request):
    context={}
    if request.method == 'POST':
        post_data = request.POST
        data = {}
        data = post_data.get('data', None)
        if data:
            return redirect('%s?%s' % (reverse('home'),
                                urllib.parse.urlencode({'q': data})))

    elif request.method == 'GET':
        get_data = request.GET
        data = get_data.get('q',None)

        if not data:
            return render(request,
                'mybook/home.html', context)

        print('load data...')

        df = pd.DataFrame(BookData.objects.all().values())

        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(df['keyword'])
        cosine_sim = cosine_similarity(count_matrix, count_matrix)
        indices = pd.Series(df.index, index=df['title'])

        idx = indices[data]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:6]
        book_indices = [i[0] for i in sim_scores]

        titles_query = list(df['title'].iloc[book_indices])
        context['books']= zip(titles_query,book_indices[:nbooksperquery])

        return render(request,
            'mybook/query_results.html', context)

def auth(request):
    print('auth--:', request.user.is_authenticated)
    if request.method == 'GET':
        data = request.GET
        auth_method = data.get('auth_method')
        if auth_method=='sign in':
           return render(request,
               'mybook/signin.html',  {})
        else:
            return render(request,
                'mybook/createuser.html', {})
    elif request.method == 'POST':
        post_data = request.POST
        name = post_data.get('name', None)
        pwd = post_data.get('pwd', None)
        pwd1 = post_data.get('pwd1', None)
        print ('auth:',request.user.is_authenticated)
        create = post_data.get('create', None)#hidden input
        if name and pwd and create:
           if User.objects.filter(username=name).exists() or pwd!=pwd1:
               return render(request,
                   'mybook/userexistsorproblem.html')
           user = User.objects.create_user(username=name,password=pwd)
           uprofile = UserProfile()
           uprofile.user = user
           uprofile.name = user.username
           uprofile.save(create=True)
           user = authenticate(username=name, password=pwd)
           login(request, user)
           return render(request,'mybook/home.html')
        elif name and pwd:
            user = authenticate(username=name, password=pwd)
            if user:
                login(request, user)
                return render(request,
                    'mybook/home.html')
            else:
                #notfound
                return render(request,
                    'mybook/nopersonfound.html')

def signout(request):
    logout(request)
    return render(request,
        'mybook/home.html')

def author(request):
    context={}
    if request.method == 'POST':
        post_data = request.POST
        data = {}
        data = post_data.get('data', None)
        if data:
            return redirect('%s?%s' % (reverse('author'),
                                urllib.parse.urlencode({'q': data})))
    elif request.method == 'GET':
        get_data = request.GET
        author = get_data.get('q',None)

        if not author:
            return render(request,
                'mybook/author.html', context)

        author_book_list = []
        bobj = BookData.objects.filter(author=author)
        for obj in bobj[:]:
            author_book_list.append(obj.title)

        context['books']=author_book_list
        return render(request,
            'mybook/author_results.html', context)

def genre(request):
    context={}
    if request.method == 'POST':
        post_data = request.POST
        data = {}
        data = post_data.get('data', None)
        if data:
            return redirect('%s?%s' % (reverse('genre'),
                                urllib.parse.urlencode({'q': data})))
    elif request.method == 'GET':
        get_data = request.GET
        genre = get_data.get('q',None)

        if not genre:
            return render(request,
                'mybook/genre.html', context)

        genre_book_list = []
        bobj = BookData.objects.filter(genre=genre)
        for obj in bobj[:]:
            genre_book_list.append(obj.title)

        context['books']=genre_book_list[:10]
        return render(request,
            'mybook/genre_results.html', context)

def view_list(request):
    context={}
    if request.method == 'GET':
        get_data = request.GET
        userprofile = UserProfile.objects.get(user=request.user)

        titles_list = []
        if ListBook.objects.filter(user=userprofile).exists():
            bobj = ListBook.objects.filter(user=userprofile)
            for obj in bobj[:]:
                titles_list.append(obj.book)

        context['books']= titles_list
        return render(request,
            'mybook/view_list.html', context)


def delete_book(request):
    data = request.GET
    book = data.get('book')
    userprofile = UserProfile.objects.get(user=request.user)
    ListBook.objects.filter(book=book,user_id=userprofile.id).delete()

    return render(request, 'mybook/delete_success.html', {})

def add_list(request):
    userprofile = UserProfile.objects.all()
    if request.method == 'POST':
        post_data = request.POST
        mytitle = post_data.get('title', None)
        addmylist = post_data.get('add', None)#hidden input
        userprofile = UserProfile.objects.get(user=request.user)
        if mytitle and addmylist:
            bl = ListBook();
            bl.user = userprofile
            bl.book = mytitle
            bl.save()

    return render(request, 'mybook/add_list.html', {})

def books_recs(request):
    userprofile = None
    print ('uuuu:',request.user.is_superuser)
    if request.user.is_superuser:
        return render(request,
            'mybook/superusersignin.html',{})
    elif request.user.is_authenticated:
        userprofile = UserProfile.objects.get(user=request.user)
    else:
        return render(request,
            'mybook/pleasesignin.html', {})

    context = {}

    req_user = UserProfile.objects.get(user=request.user)
    userprofile = UserProfile.objects.all()
    countuser = userprofile.count()
    users_interests = []
    for u in range(1,countuser+1):
        titles_list = []
        bobj = ListBook.objects.filter(user_id=u)
        for obj in bobj[:]:
            titles_list.append(obj.book)
        users_interests.append(titles_list)

    # user-based CF filtering 구현
    def cosine_similarity(v, w):
        return np.dot(v, w) / math.sqrt(np.dot(v, v) * np.dot(w, w))

    unique_interests = sorted(list({interest
                                    for user_interests in users_interests
                                    for interest in user_interests}))

    def make_user_interest_vector(user_interests):
        return [1 if interest in user_interests else 0
                for interest in unique_interests]

    user_interest_vectors = [make_user_interest_vector(user_interests)
                              for user_interests in users_interests]

    user_similarities = [[cosine_similarity(interest_vector_i, interest_vector_j)
                        for interest_vector_j in user_interest_vectors]
                        for interest_vector_i in user_interest_vectors]

    def most_similar_users_to(user_id):
        pairs = [(other_user_id, similarity) # find other
            for other_user_id, similarity in # users with
                enumerate(user_similarities[user_id]) # nonzero
            if user_id != other_user_id and similarity > 0] # similarity

        return sorted(pairs, # sort them
                key=lambda pair: pair[-1], # most similar
                reverse=True) # first

    def user_based_suggestions(user_id, include_current_interests=False):
        suggestions = defaultdict(float)
        for other_user_id, similarity in most_similar_users_to(user_id):
            for interest in users_interests[other_user_id]:
                suggestions[interest] += similarity

        suggestions = sorted(suggestions.items(),
                             key = lambda pair: pair[-1],
                             reverse = True)

        print(suggestions)
        if include_current_interests:
            return suggestions
        else:
            return [(i[0])
                    for i in suggestions
                    if i[0] not in users_interests[user_id]]

    rec_query = user_based_suggestions(req_user.id-1)
    context['recs'] = rec_query
    return render(request,
        'mybook/recommendations.html', context)
