'''
Author: Henry Yeomans
Created: 2021-01-20

Class: BHOScraper
-----------------
- A simple webscraping bot. It's aim is to collect the title, publication name and excerpt from
  the results of a word search query of the "https://www.british-history.ac.uk/catalogue" collection
  of document series.
'''
#%%
import re
import requests
import os
import time
import numpy as np
import pandas as pd
import pickle 

from urllib.parse import quote_plus
from tqdm import tqdm as tqdm
from bs4 import BeautifulSoup


def save_item_to_path(item, path, file_name):
    try:
        if not os.path.exists(path):
            os.mkdir(path)
        pickle_path = os.path.join(path, file_name)
        with open(pickle_path, 'wb') as f:
            pickle.dump(item, f)
    except:
        raise ValueError('Please enter a valid path.')


def change_href(href):
    '''
    Performs necessary replacement "/" -> "--" in the href given in 
    catalogue html.
    '''
    href = '/' + href[1:].replace('/', '--')
    return href


def standardize_query(query):
    p = re.compile(r'[\W_]+')
    return p.sub('', query).lower()

class BHOScraper():

    def __init__(self):
        self.scraped_series = []
        self.catalogue = {}
        self.scraped_series = {}


    def scrape_catalogue(self, path=None):
        '''
        Collects series in BHO catalogue into a dictionary
        
        If path is given, the dictionary will be saved as a *.pickle to the path.
        
        Returns: None
        '''
        catalogue      = self.catalogue
        if catalogue:
            raise Exception('Catalogue already exists. Reset using "self.reset_catalogue" before scraping again.')
            return None

        catalogue_url  = r'https://www.british-history.ac.uk/catalogue'
        try:
            catalogue_get  = requests.get(catalogue_url)
        except:
            raise Exception('Unknown error. Please try again.')
        status_code    = catalogue_get.status_code
        if status_code != 200:
            raise Exception('Error: status code: {}'.format(status_code))
        catalogue_html = catalogue_get.text
        catalogue_soup = BeautifulSoup(catalogue_html, 'html.parser')
        table_contents = catalogue_soup.find('table')
        table_rows     = table_contents.find_all('tr')
        for row in table_rows[1:]:
            p            = re.compile(r'[\W_]+')
            series_title = row.find_all('a')[0].text
            series_title = p.sub('', series_title).lower()
            series_href  = row.find_all('a')[0]['href']
            series_href  = change_href(series_href)
            pattern      = re.compile(r'no-series')
            if not pattern.findall(series_href):
                catalogue[series_title] = r'https://www.british-history.ac.uk/search/series' + series_href + r'?query={}&page={}'
        if path:
            save_item_to_path(catalogue, path, 'catalogue.pickle')

        # Now update the catalogue attribute
        self.catalogue = catalogue

        return None


    def reset_catalogue(self):
        '''
        Resets catalogue to an empty dict and deletes catalogue.pickle file if found.
        '''
        if self.catalogue.keys():
            catalogue_path = os.path.join('.', 'catalogue', 'catalogue.pickle')
            if os.path.exists(catalogue_path):
                os.remove(catalogue_path)
            self.catalogue = {}

        return None


    def search_for_series(self, series_query):
        '''
        Finds the base url for a given series title: series_query (string).
        
        Returns: base_url (string), series_name (string)
        '''
        if type(series_query) != str:
            raise ValueError('"series_query" must be a string.')

        # Standardize query

        series_query_std = standardize_query(series_query)

        if self.catalogue:
            # Search the catalogue for series_query
            catalogue = self.catalogue
            try:
                base_url    = catalogue[series_query_std]
                pattern     = re.compile(r'uk/.+\?')
                series_name = pattern.findall(base_url)[-1][7:-1].replace('/', '-')
                return base_url, series_name
            except Exception as e:
                print(e)
                return None, None
        else:
            print('No catalogue exists locally. Collecting from "https://www.british-history.ac.uk/catalogue"')
            # Scrape the catalogue into a dictionary
            self.scrape_catalogue()
            # Now search for the query
            return self.search_for_series(series_query)


    def scrape_results(self, url):
        '''
        Collects query search results on page given by url.
        
        Returns: pandas.DataFrame with columns ['title', 'publication', 'excerpt']
        '''
        # Request html and create soup object
        page_html = requests.get(url).text
        soup = BeautifulSoup(page_html, 'html.parser')

        # Look for the view-content section
        tag = 'div'
        attributes = {'class' : 'view-content'}
        view_content = soup.find('div', {'class' : 'region region-content'}).find(tag, attributes)
        
        # Create dictionary to be filled with scraped data
        content = {'title' : [], 'publication' : [], 'excerpt' : []}
        
        # Scrape data from each row
        for row in view_content.find_all('div', recursive=False):

            # Find the title:
            title_tag = 'h4'
            title_attributes = {'class' : 'title'}
            title = row.find(title_tag, title_attributes, recursive=False)
            try:
                title = title.find('a').text
            except:
                title = np.nan

            # Find the publication
            publication_excerpt_tag = 'p'
            publication_attributes = {'class' : 'publication'}
            try:
                publication = row.find(publication_excerpt_tag, publication_attributes).text
            except:
                publication = np.nan

            # Find the excerpt 
            excerpt_attributes = {'class' : 'excerpt'}
            try:
                excerpt = row.find(publication_excerpt_tag, excerpt_attributes).text
            except:
                excerpt = np.nan        
            # Now append to dictionary values
            content['title'].append(title)
            content['publication'].append(publication)            
            content['excerpt'].append(excerpt)

        # Create dataframe containing scraped data
        df = pd.DataFrame(content)

        return df


    def scrape_series(self, series_queries, queries, path=None):
        '''
        Scrapes the title, publication and excerpt text from the series result retrurned by 
        searching for 'series_query' (string) which contain words in 'queries' (iterable). 
        
        Updates "scraped_series" (dict) attribute to contain a pandas.DataFrame object
        for each series_query.

        If path is given, saves data to <catalogue_url_reference>.csv file at path with columns: 
        ['query', 'title', 'publication', 'excerpt'] for each series_query.
        
        Returns: None
        '''
        if type(queries) == str:
            queries = [queries]
        elif type(queries) != list:
            try:
                queries = list(query)
            except:
                raise ValueError('Invalid "queries" entered.')
        if type(series_queries) == str:
            series_queries = [series_queries]
        elif type(series_queries) != list:
            try:
                series_queries = list(series_queries)
            except:
                raise ValueError('Invalid "series_queries" entered.')
        
        for series_query in series_queries:
            query_dfs = []
            for query in queries:
                print('Searching "{}" for "{}"...'.format(series_query, query))
                base_url, series_name = self.search_for_series(series_query)
                

                try:
                    first_page_url = base_url.format(quote_plus(query), 0)

                        

                    r = requests.get(first_page_url)

                    first_page = r.text
                    first_page_soup = BeautifulSoup(first_page, 'html.parser')
                    last_page_tag = 'a'
                    last_page_attributes = {'title' : 'Go to last page'}

                    try:
                        last_page     = first_page_soup.find(last_page_tag, last_page_attributes)
                        last_page_url = last_page['href']
                        pattern       = re.compile(r'&page=[0-9]+')
                        num_pages     = int(pattern.findall(last_page_url)[0][6:])
                        dfs           = [self.scrape_results(first_page_url)]
                    except:
                        print('No results for "{}" in "{}"'.format(query, series_query))
                        num_pages = 0
                        dfs       = []

                    for i in tqdm(range(1, num_pages + 1)):
                        df = self.scrape_results(base_url.format(quote_plus(query), i))
                        dfs.append(df)

                    if dfs:
                        query_df = pd.concat(dfs, axis=0)
                        query_df['query'] = query
                        query_df = pd.concat([query_df.iloc[:,-1], query_df.iloc[:,:-1]], axis=1)
                        query_dfs.append(query_df)
                except:
                    pass
            if query_dfs:
                series_df = pd.concat(query_dfs, axis=0)
                if series_query in self.scraped_series.keys():
                    df_existing = self.scraped_series[series_query]
                    series_df = pd.concat([df_existing, series_df], axis=0, ignore_index=True)
                series_df.drop_duplicates(inplace=True, ignore_index=True)
                self.scraped_series[series_query] = series_df
                if path:
                    try:
                        if not os.path.exists(path):
                            os.mkdir(path)
                        save_location = os.path.join(path, '{}.csv'.format(series_name))
                        series_df.to_csv(save_location, index=False)
                    except:
                        raise ValueError('Please enter a valid path.')
            else:
                print('No results for any of "queries" in {}.'.format(series_query))

        return None  



# %%
