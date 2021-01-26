# -*- coding: utf-8 -*-

import pytest
import mock

from bho_scraper import bho_scraper


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
    # ======================== test_scrape_catalogue =======================================
    mock_text = '''<html>
                        <body>
                            <table>
                                <tbody>
                                    <tr>
                                        <td>
                                            <a>First row not taken</a>    
                                        </td>
                                        <td>
                                            First row not taken 
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <a href="/yes/series/test">Yes Series Test</a>    
                                        </td>
                                        <td>
                                            Single volume    
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <a href="/no-series/no_series_test">No Series Test</a>    
                                        </td>
                                        <td>
                                            Single volume    
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </body>
                    </html>
                ''' 
    correct_scraped_catalogue = {
        'yesseriestest' : 'https://www.british-history.ac.uk/search/series/yes--series--test?query={}&page={}'
    }

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
    for actual_key, expected_key in zip(actual_result.keys(), expected_result.keys()):
        assert actual_key == expected_key
    for actual_value, expected_value in zip(actual_result.values(), expected_result.values()):
        assert actual_value == expected_value


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





