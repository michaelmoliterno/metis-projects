__author__ = 'michaelmoliterno'


import urllib2
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
import pickle
import time
from random import randint
import dateutil.parser
import operator
import numpy as np
from pandasql import sqldf




def get_bom_alpha_urls():

    try:
        all_urls = []
        all_letters = ['A','B','C','D','E','F','G','H','I',
                       'J','K','L','M','N','O','P','Q','R',
                       'S','T','U','V','W','X','Y','Z','NUM']

        for letter in all_letters:
            movies_url = "http://boxofficemojo.com/movies/alphabetical.htm?letter="+letter+"&p=.htm"
            all_urls.append(movies_url)
            page = urllib2.urlopen(movies_url)
            soup = BeautifulSoup(page)
            for link in soup.find(class_='alpha-nav-holder').find_all('a'):
                all_urls.append('http://boxofficemojo.com/'+ link.get('href'))

        return all_urls
    except:
        return None


def get_all_bom_urls(bom_alpha_urls):
    try:
        master_movies_list = []

        for i in range(len(bom_alpha_urls)):
            movies_url = bom_alpha_urls[i]
            page = urllib2.urlopen(movies_url)
            soup = BeautifulSoup(page)
            for link in soup.find_all('a'):
                link_string = link.get('href')
                m = re.search(r'/movies/\?id',link_string)
                if m:
                    master_movies_list.append('http://boxofficemojo.com'+link_string)

        # This returns a list free of duplicates.
        master_movies_list = sorted(list(set(master_movies_list)))

        # This cleans some irregularities in the URLs
        for i in range(len(master_movies_list)):
            master_movies_list[i] = re.sub('\xa0','%A0',master_movies_list[i])

        return master_movies_list

    except:
        return None

def get_movie_value(soup, field_name):

    try:

        obj = soup.find(text=re.compile(field_name))

        if not obj:
            return None

        next_sibling = obj.findNextSibling()
        if next_sibling:

            if field_name == 'Production Budget':
                return next_sibling.text
#                 print next_sibling.text.split()[0]
#                 budget = money_to_int(next_sibling.text.split()[0])
#                 if budget is not None:
#                     return budget*1000000
#                 else:
#                     return budget


            else:
                return next_sibling.text


        else:
            return None
    except:
        return None

def get_title(soup):
    try:
        title_string=soup.find('title').text
        title = title_string.split('(')[0].strip()
        return title
    except:
        return None

# def get_director(soup):
#     try:
#         urls_test = soup.find_all('a')
#         for link in urls_test:
#             link_string = link.get('href')
#             sub_director = re.search(r'people/chart/\?view=Director', link_string)
#             if sub_director:
#                 director = link.text
#                 return director
#         return None
#     except:
#         return None


def get_widest_release(soup):
    widest_release = None
    try:
        movie_revs = soup.find_all(class_='mp_box_content')
        for td in movie_revs[1].find_all('td'):
            widest_release_search = re.search(r'Widest\xa0Release:',td.text)
            if widest_release_search:
                widest_release = money_to_int(td.nextSibling.nextSibling.text.split()[0])
        return widest_release
    except:
        return widest_release


def get_in_release(soup):
    in_release = None
    try:
        movie_revs = soup.find_all(class_='mp_box_content')
        for td in movie_revs[1].find_all('td'):
            in_release_search = re.search(r'In Release:',td.text)
            if in_release_search:
                in_release = td.nextSibling.nextSibling.text.split()[0]
        return in_release
    except:
        return in_release


def get_close_date(soup):
    close_date = None
    try:
        movie_revs = soup.find_all(class_='mp_box_content')
        for td in movie_revs[1].find_all('td'):
            close_date_search = re.search(r'Close\xa0Date:',td.text)
            if close_date_search:
                close_date = to_date(td.nextSibling.nextSibling.text.strip())

        return close_date
    except:
        return close_date


def get_genres(soup):
    genres = ''
    try:

        for mp_box_tab in soup.find_all(class_='mp_box_tab'):
            if mp_box_tab.text == 'Genres':
                for genre in mp_box_tab.parent.findAll('a'):
                    genres = genres + genre.text + ';'
        return genres
    except:
        return genres


def get_domestic_gross(soup):
    domestic_gross=0
    try:
        domestic_rev = soup.find_all(class_='mp_box_content')
        for td in domestic_rev[0].find_all('td'):
            domestic = re.search(r'Domestic', td.text)
            if domestic:

                rev = money_to_int(td.nextSibling.nextSibling.text.strip())

                if rev is not None:
                    domestic_gross = rev
                else:
                    domestic_gross = 0
        return domestic_gross
    except:
        return -1


def get_foreign_gross(soup):
    foreign_gross=0
    try:
        foreign_rev = soup.find_all(class_='mp_box_content')
        for td in foreign_rev[0].find_all('td'):
            foreign = re.search(r'Foreign', td.text)
            if foreign:
                rev= money_to_int(td.nextSibling.nextSibling.text.strip())

                if rev is not None:
                    foreign_gross = money_to_int(td.nextSibling.nextSibling.text)
                else:
                    foreign_gross=0
        return foreign_gross
    except:
        return -1



def get_players(soup):

    players = ''

    search_strings = [('Director', r'\?view=Director&id='),('Actor',r'\?view=Actor&id='),('Writer',r'\?view=Writer&id='),
                      ('Producer',r'\?view=Producer&id='), ('Composer',r'\?view=Composer&id='),
                      ('Cinematographer',r'\?view=Cinematographer&id=')]

    for string in search_strings:
        for href in soup.find_all('a'):
            link_string = href.get('href')

            directors = re.search(string[1],link_string)
            if directors:
                players = players+string[0] + ':' + href.text.replace('*','').strip() + ';'
#                 if string[0] not in players:
#                     players[string[0]] = [href.text.replace('*','').strip()]
#                 else:
#                     players[string[0]].append(href.text.replace('*','').strip())



    return players




## helpful helper methods

def to_date(datestring):
    try:
        date = dateutil.parser.parse(datestring)
        return date
    except:
        return dateutil.parser.parse('January 1, 3000')

def money_to_int(moneystring):
    try:
        moneystring = moneystring.replace('$','').replace(',','')
        return int(moneystring)
    except:
        return None

def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0])*60 + int(runtime[2])
        return minutes
    except:
        return None



def scrape_bom(movie_urls):

    url_count=0
    opened=0
    skipped=0

    movie_data = []
    skipped_urls = []

    headers = ['movie_title','players','genres','budget','domestic_total_gross','foreign_total_gross','release_date','close_date',
               'runtime_mins','rating','distributor','widest_release','in_release','movie_url']

    for i in range(len(movie_urls)):

        url_count+=1

        if url_count%100==0:
            sleep = randint(5,15)
            print "sleeping for %s seconds" %sleep
            time.sleep(sleep)
            print 'processed:',opened
            print 'skipped',skipped
            pickle.dump(movie_data, open("mojo_scrape.p", "wb" ))
            pickle.dump(skipped_urls, open("mojo_scrape_skipped.p", "wb" ) )


        movies_url = movie_urls[i]

        try:

            page = urllib2.urlopen(movies_url)
            opened += 1
            soup = BeautifulSoup(page)
            title = get_title(soup)
            players = get_players(soup)
            genres = get_genres(soup)
            prod_budget = get_movie_value(soup, 'Production Budget')
            domestic_total_gross = get_domestic_gross(soup)
            foreign_total_gross = get_foreign_gross(soup)
            release_date = to_date(get_movie_value(soup, 'Release Date'))
            close_date = get_close_date(soup)
            runtime = runtime_to_minutes(get_movie_value(soup, 'Runtime'))
            rating = get_movie_value(soup, 'MPAA Rating')
            distributor = get_movie_value(soup, 'Distributor')
            widest_release = get_widest_release(soup)
            in_release = get_in_release(soup)

            movie_dict= dict(zip(headers,[title,players,genres,prod_budget,domestic_total_gross,foreign_total_gross,release_date,
                        close_date,runtime,rating,distributor,widest_release,in_release,movies_url]))

            movie_data.append(movie_dict)


        except:
            print 'error processing', movies_url
            skipped += 1
            skipped_urls.append(movies_url)


    pickle.dump(movie_data, open("mojo_scrape.p", "wb" ))
    pickle.dump(skipped_urls, open("mojo_scrape_skipped.p", "wb" ) )
    return movie_data




def set_season(x):
    if x in [5,6,7]:
        return 'summer'
    elif x in [11,12]:
        return 'holiday'
    else:
        return 'off'


def get_movies_with_budget(movies_df):
    # from pandasql import sqldf
    #pysqldf = lambda q: sqldf(q, globals())

    movies_df['budget_int'] = 0

    #print movies_df.head()

    # These movies have budgets formatted: '$XX million'
    q = "SELECT * FROM movies_df where release_date > '1990-01-01 00:00:00' and release_date < '2014-11-01 00:00:00' and budget like '%million%' and widest_release >0;"

    movies_budget_over_mil =  sqldf(q,locals());


    # These movies have budgets formatted $X,XXX,XXX with the maximum value of one million
    q= "SELECT * FROM movies_df where release_date > '1990-01-01 00:00:00' and release_date < '2014-11-01 00:00:00' and budget not like '%million%' and budget not like 'N/A' and widest_release >0;"

    movies_budget_under_mil =  sqldf(q,locals());

    ### clean up the budgets, convert to INT
    for index,row in movies_budget_over_mil.iterrows():
        movies_budget_over_mil.ix[index,'budget_int'] = float(row['budget'].split()[0].replace('$',''))*1000000

    for index,row in movies_budget_under_mil.iterrows():
        movies_budget_under_mil.ix[index,'budget_int'] = float(row['budget'].replace('$','').replace(',',''))

    movies_df = movies_budget_over_mil.append(movies_budget_under_mil,ignore_index = True)

    ### add values that we will need for future processing
    movies_df['ones'] = 1.0
    movies_df['total_gross'] = 0.0

    for players in ['actors','directors','writers','producers']:
        movies_df[players] = ''

    movies_df['release_month'] = pd.DatetimeIndex(movies_df['release_date']).month
    movies_df['season'] = movies_df['release_month'].map(lambda x: set_season(x))

    return movies_df

def deflate_dollar_values(movies_df):


    ## we need these data to convert to 2014 dollars

    cpi = pd.read_csv('CPI-2005.csv')
    cpi['inflator'] = 0

    for index, row in cpi.iterrows():
        cpi.ix[index,'inflator'] = 121.2/row['CPI2005base']
        cpi.ix[index,'Date'] = row['Date'].split('/')[2]

    cpi_date_indexed = cpi.set_index('Date')


    ## convert all $ values to 2014 dollars

    for index,row in movies_df.iterrows():

        year = str(row['release_date'].year)

        if year in cpi.index.values:
            inflator = cpi_date_indexed.loc[year]['inflator']
            cpi.ix[index,'foreign_total_gross'] = row['foreign_total_gross']*inflator
            cpi.ix[index,'domestic_total_gross'] = row['domestic_total_gross']*inflator
            cpi.ix[index,'budget_int'] = row['budget_int']*inflator

    ## calculate the total (worldwide) gross for a movie
    for index,row in movies_df.iterrows():
        movies_df.ix[index,'total_gross'] = row['domestic_total_gross'] + row['foreign_total_gross']


    movies_df['log_total_gross'] = np.log1p(movies_df['total_gross'])
    movies_df['log_domestic_gross'] = np.log1p(movies_df['domestic_total_gross'])
    movies_df['log_foreign_gross'] = np.log1p(movies_df['foreign_total_gross'])
    movies_df['log_budget'] = np.log1p(movies_df['budget_int'])
    movies_df['log_widest_release'] = np.log1p(movies_df['widest_release'])
    #movies_df['log_in_release'] = np.log1p(movies_df['in_release'])

    return movies_df

### this puts the playrs in their own column and semi-colon delimited
def separate_players(movies_df):
    for index,row in movies_df.iterrows():

        actors = []
        directors = []
        writers = []

        for player in row['players'].split(';'):
            player_type = player.split(':')[0]
            if player_type == 'Actor':
                actors.append('actor_'+player.split(':')[1].replace(" ", "").replace(".","").replace("&",""))
            elif player_type == 'Director':
                directors.append('director_'+player.split(':')[1].replace(" ", "").replace(".","").replace("&",""))
            elif player_type == 'Writer':
                writers.append('writer_'+player.split(':')[1].replace(" ", "").replace(".","").replace("&",""))

        movies_df.ix[index, 'actors'] = ';'.join(actors)
        movies_df.ix[index, 'directors'] =  ';'.join(directors)
        movies_df.ix[index, 'writers'] =  ';'.join(writers)

    return movies_df


### count the genres in the model
def add_genres_columns(movies_df, min_occurances=20):
    genres_count = {}

    for index,row in movies_df.iterrows():

        for genre in row['genres'].split(';'):
            if len(genre.split()):
                genre_movie = genre.split()[0]
                if genre_movie not in genres_count.keys():
                    genres_count[genre_movie] = 1
                else:
                    genres_count[genre_movie] = genres_count[genre_movie] + 1

    model_genres = []
    sorted_genres = sorted(genres_count.items(), key=operator.itemgetter(1), reverse=True)
    for genre in sorted_genres:
        if genre[1]>=min_occurances:
            model_genres.append(genre[0])

    ### and this adds them to the model
    for genre in model_genres:
        movies_df[genre] = 0


    # adds the genres
    for index,row in movies_df.iterrows():

        for genre in row['genres'].split(';'):
            if len(genre.split()):
                genre_movie = genre.split()[0]
                for model_genre in model_genres:
                    if genre_movie == model_genre:
                        movies_df.ix[index, model_genre] = 1

    return movies_df, model_genres


def dummify_players(movies_df,min_occurances=5):

    ### this creates a dictionary of all of the players in our dataset

    all_actors = {}
    all_directors = {}
    all_writers = {}

    for index,row in movies_df.iterrows():

        for writer in row['writers'].split(';'):
            if writer != '':
                if writer not in all_writers.keys():
                    all_writers[writer] = 1
                else:
                    all_writers[writer] = all_writers[writer] + 1

        for actor in row['actors'].split(';'):
            if actor != '':
                if actor not in all_actors.keys():
                    all_actors[actor] = 1
                else:
                    all_actors[actor] = all_actors[actor] + 1

        for director in row['directors'].split(';'):
            if director != '':
                if director not in all_directors.keys():
                    all_directors[director] = 1
                else:
                    all_directors[director] = all_directors[director] + 1


    ###this creates a list of writers that will be added to the model
    model_writers = []
    sorted_writers = sorted(all_writers.items(), key=operator.itemgetter(1), reverse=True)

    for writer in sorted_writers:
        if writer[1]>=min_occurances:
            model_writers.append(writer[0])

    for writer in model_writers:
        movies_df[writer] = 0


    for index,row in movies_df.iterrows():
        for movie_writer in row['writers'].split(';'):
            for model_writer in model_writers:
                if movie_writer == model_writer:
                    movies_df.ix[index, model_writer] = 1


    ###this creates a list of actors that will be added to the model
    model_actors = []
    sorted_actors = sorted(all_actors.items(), key=operator.itemgetter(1), reverse=True)

    for actor in sorted_actors:
        if actor[1] >= min_occurances:
            model_actors.append(actor[0])

    for actor in model_actors:
        movies_df[actor] = 0


    for index,row in movies_df.iterrows():
        for movie_actor in row['actors'].split(';'):
            for model_actor in model_actors:
                if movie_actor == model_actor:
                    movies_df.ix[index, model_actor] = 1


    ###this creates a list of directors that will be added to the model
    model_directors = []
    sorted_directors = sorted(all_directors.items(), key=operator.itemgetter(1), reverse=True)

    for director in sorted_directors:
        if director[1] >= min_occurances:
            model_directors.append(director[0])


    for director in model_directors:
        movies_df[director] = 0

    for index,row in movies_df.iterrows():
        for movie_director in row['directors'].split(';'):
            for model_director in model_directors:
                if movie_director == model_director:
                    movies_df.ix[index, model_director] = 1

    return movies_df, model_actors, model_directors, model_writers



