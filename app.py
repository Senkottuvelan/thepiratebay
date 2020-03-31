'''
This is the main module
'''
import os

import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime, timedelta


APP = Flask(__name__)
CORS(APP)
EMPTY_LIST = []

BASE_URL = os.getenv('BASE_URL', 'https://thepiratebay.org/')
JSONIFY_PRETTYPRINT_REGULAR = True

# Translation table for sorting filters
sort_filters = {
    'title_asc': 1,
    'title_desc': 2,
    'time_desc': 3,
    'time_asc': 4,
    'size_desc': 5,
    'size_asc': 6,
    'seeds_desc': 7,
    'seeds_asc': 8,
    'leeches_desc': 9,
    'leeches_asc': 10,
    'uploader_asc': 11,
    'uploader_desc': 12,
    'category_asc': 13,
    'category_desc': 14
}


@APP.route('/', methods=['GET'])
def index():
    '''
    This is the home page and contains links to other API
    '''
    return render_template('index.html'), 200


@APP.route('/top/', methods=['GET'])
@APP.route('/top48h/', methods=['GET'])
def default_top():
    '''
    Returns default page with categories
    '''
    return render_template('top.html'), 200


@APP.route('/top/<int:cat>/', methods=['GET'])
def top_torrents(cat=0):
    '''
    Returns top torrents
    '''

    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''

    if cat == 0:
        url = BASE_URL + 'top/' + 'all/' + str(sort_arg)
    else:
        url = BASE_URL + 'top/' + str(cat) + '/' + str(sort_arg)
    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/top48h/<int:cat>/', methods=['GET'])
def top48h_torrents(cat=0):
    '''
    Returns top torrents last 48 hrs
    '''

    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''

    if cat == 0:
        url = BASE_URL + 'top/48h' + 'all/'
    else:
        url = BASE_URL + 'top/48h' + str(cat)

    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/recent/', methods=['GET'])
@APP.route('/recent/<int:page>/', methods=['GET'])
def recent_torrents(page=0):
    '''
    This function implements recent page of TPB
    '''
    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''

    url = BASE_URL + 'recent/' + str(page)
    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/api-search/', methods=['GET'])
def api_search():
    url = BASE_URL + 's/?' + request.query_string.decode('utf-8')
    return jsonify(parse_page(url)), 200


@APP.route('/search/', methods=['GET'])
def default_search():
    '''
    Default page for search
    '''
    return 'No search term entered<br/>Format for search: /search/search_term/page_no(optional)/'


@APP.route('/search/<term>/', methods=['GET'])
@APP.route('/search/<term>/<int:page>/', methods=['GET'])
def search_torrents(term=None, page=0):
    '''
    Searches TPB using the given term. If no term is given, defaults to recent.
    '''

    sort = request.args.get('sort')
    sort_arg = sort_filters[request.args.get('sort')] if sort in sort_filters else ''

    url = BASE_URL + 'search/' + str(term) + '/' + str(page) + '/' + str(sort_arg)
    return parse_page(url), 200


def parse_page(url, sort=None):
    '''
    This function parses the page and returns list of torrents
    '''
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'lxml')
    table_present = soup.find('table', {'id': 'searchResult'})
    if table_present is None:
        return EMPTY_LIST
   # titles = parse_titles(soup)
    links = parse_links(soup)
   # magnets = parse_magnet_links(soup)
   # times, sizes, uploaders = parse_description(soup)
   # seeders, leechers = parse_seed_leech(soup)
   # cat, subcat = parse_cat(soup)
   
    return links

def parse_magnet_links(soup):
    '''
    Returns list of magnet links from soup
    '''
    magnets = soup.find('table', {'id': 'searchResult'}).find_all('a', href=True)
    magnets = [magnet['href'] for magnet in magnets if 'magnet' in magnet['href']]
    return magnets





def parse_links(soup):
    '''
    Returns list of links of torrents from soup
    '''
    links = soup.find_all('a', class_='detLink', href=True)
    links[:] = [link['href'] for link in links]
    return links


