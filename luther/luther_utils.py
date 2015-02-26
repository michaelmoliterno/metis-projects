__author__ = 'michaelmoliterno'


import urllib2
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import pickle
import time
from random import randint
import dateutil.parser


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
            pickle.dump(movie_data, open("mojo_scrub.p", "wb" ))
            pickle.dump(skipped_urls, open("mojo_scrub_skipped.p", "wb" ) )


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


    pickle.dump(movie_data, open("mojo_scrub.p", "wb" ))
    pickle.dump(skipped_urls, open("mojo_scrub_skipped.p", "wb" ) )