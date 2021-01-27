# -*- coding: utf-8 -*-

import pytest
import mock
import pandas as pd
import numpy as np
import requests

from bho_scraper import bho_scraper
from flask import Flask, request
from tests.conftest import WebServer


class Store:
    # ======================== test_change_href =======================================
    mock_href = r'/test/href'
    correct_changed_href = r'/test--href'
    # ======================================================================================
    # ======================== test_standardize_query =======================================
    mock_query = r'test QUery here ##::;___'
    correct_standardized_query = r'testqueryhere'
    # ======================================================================================
    # ======================== test_search_for_series ======================================
    mock_series_query = r'test series query'
    mock_catalogue = {r'testseriesquery' : r'http://mock_base_url.co.uk/abc/example/href?'}
    correct_search_return = (r'http://mock_base_url.co.uk/abc/example/href?', 'example-href')
    # ======================================================================================
    # ======================== test_scrape_catalogue =======================================
    mock_text = '''
                    <html><body><table><tbody><tr><td><a>First row not taken</a></td><td>
                    First row not taken</td></tr><tr><td><a href="/yes/series/test">Yes
                    Series Test</a></td><td>Single volume</td></tr><tr><td>
                    <a href="/no-series/no_series_test">No Series Test</a> </td>
                    <td>Single volume</td></tr></tbody></table></body></html>
                ''' 
    correct_scraped_catalogue = {
        'yesseriestest' : 'https://www.british-history.ac.uk/search/series/yes--series--test?query={}&page={}'
    }
    # ======================================================================================
    # ======================== test_scrape_results =======================================
    mock_results_html1 = '''
                            <html><body><div class="region region-content"><div class="view-content">
                            <div>
                            <h4 class="title"><a>Test Title 1</a></h4>
                            <p class="publication">Test Publication 1</p>
                            <p class="excerpt">Test Excerpt 1</p>
                            </div>
                            <div>
                            <h4 class="title"><a>Test Title 2</a></h4>
                            <p class="publication">Test Publication 2</p>
                            </div>
                            <div>
                            <h4 class="title"><a>Test Title 3</a></h4>
                            <p class="excerpt">Test Excerpt 3</p>
                            </div>
                            <div>
                            <h4 class="title"></h4>
                            <p class="publication">Test Publication 4</p>
                            <p class="excerpt">Test Excerpt 4</p>
                            </div>
                            <a title="Go to last page" href="/query=?&page=1">last</a>
                            </div></div></body></html>
                         '''
    correct_dict = {
        'title'       : ['Test Title 1', 'Test Title 2', 'Test Title 3', np.nan],
        'publication' : ['Test Publication 1', 'Test Publication 2', np.nan, 'Test Publication 4'],
        'excerpt'     : ['Test Excerpt 1', np.nan, 'Test Excerpt 3', 'Test Excerpt 4'] 
        }
    correct_df = pd.DataFrame(correct_dict)

    # ======================== test_scrape_series =======================================
    mock_results_html2 = '''
                            <html><body><div class="region region-content"><div class="view-content">
                            <div>
                            <h4 class="title"><a>Hello World</a></h4>
                            <p class="publication">abc 123</p>
                            <p class="excerpt">e = mc ** 2</p>
                            </div></div></body></html>
                         '''

    mock_scraped_catalogue = {'http://example.com' : 'testseriesname'}
    correct_scraped_df = pd.DataFrame(
        {
        'query'       : ['test_query']*5,
        'title'       : ['Test Title 1', 'Test Title 2', 'Test Title 3', np.nan, 'Hello World'],
        'publication' : ['Test Publication 1', 'Test Publication 2', np.nan, 'Test Publication 4', 'abc 123'],
        'excerpt'     : ['Test Excerpt 1', np.nan, 'Test Excerpt 3', 'Test Excerpt 4', 'e = mc ** 2'] 
        }
        )
    correct_scraped_series = {'test_series_name' : correct_scraped_df}
# ============================================================================================

store = Store()


def test_change_href():
    mock_href = store.mock_href
    expected_result = store.correct_changed_href
    actual_result = bho_scraper.change_href(mock_href)
    assert expected_result == actual_result   


def test_save_item_to_path():
    pass


class MockRequest:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code


def mocked_request_get(*args, **kwargs):
    return MockRequest(text=store.mock_text, status_code=200)


@mock.patch('requests.get', side_effect=mocked_request_get)
def test_scrape_catalogue(mock_):
    scraper         = bho_scraper.BHOScraper()
    scraper.scrape_catalogue()
    actual_result   = scraper.catalogue
    expected_result = store.correct_scraped_catalogue
    assert expected_result == actual_result


def test_reset_catalogue():
    scraper = bho_scraper.BHOScraper()
    scraper.catalogue = {'test' : 'catalogue'}
    scraper.reset_catalogue()
    assert not scraper.catalogue


def test_standardize_query():
    expected_result = store.correct_standardized_query
    actual_result   = bho_scraper.standardize_query(store.mock_query)
    assert expected_result == actual_result


def test_search_for_series():
    scraper = bho_scraper.BHOScraper()
    scraper.catalogue = store.mock_catalogue
    actual_result = scraper.search_for_series(store.mock_series_query)
    expected_result = store.correct_search_return
    assert expected_result == actual_result


def mocked_request_results_get(*args, **kwargs):
    return MockRequest(text=store.mock_results_html1, status_code=200)


@mock.patch('requests.get', side_effect=mocked_request_results_get)
def test_scrape_results(mock_):
    scraper = bho_scraper.BHOScraper()
    actual_result = scraper.scrape_results('https://hello-world.com/')
    print(actual_result)
    expected_result = store.correct_df
    print('=========================================')
    print(expected_result)
    assert expected_result.equals(actual_result)



@pytest.fixture(scope="module")
def scraper_server():
    app = Flask("scraper_server")
    server = WebServer(app)

    @server.app.route('/', methods=['GET', 'POST'])
    def display_page():
        page = request.args.get('page')
        query = request.args.get('query')
        if page == '0':
            html = store.mock_results_html1.replace('\n', '')
        elif page == '1':
            html = store.mock_results_html2.replace('\n', '')
        else:
            html = "<html><body><a href='/world'>world</a></body></html>"
    
        return html

    with server.run():
        yield server


class MockScraper(bho_scraper.BHOScraper):
    
    def __init__(self, scraper_server):
        super().__init__()
        self.url = scraper_server.url + r'/?query={}&page={}'
        self.catalogue = store.mock_scraped_catalogue
    def search_for_series(self, *args):
        return self.url, 'test_series_name'


def test_scrape_series(scraper_server):
    
    def mock_scraper(*args, **kwargs):
        return MockScraper(scraper_server=scraper_server)

    @mock.patch('bho_scraper.bho_scraper.BHOScraper', side_effect=mock_scraper)
    def get_scraper(mock_):
        scraper = bho_scraper.BHOScraper()
        scraper.scrape_series(['test_series_name'], ['test_query'])
        return scraper

    scraper = get_scraper()
    for key, correct_key in zip(scraper.scraped_series.keys(), store.correct_scraped_series.keys()):
        assert key == correct_key
        actual_df  = scraper.scraped_series[key].fillna('NaN substitute')
        correct_df =  store.correct_scraped_series[key].fillna('NaN substitute')

        assert actual_df.equals(correct_df)




# %%
