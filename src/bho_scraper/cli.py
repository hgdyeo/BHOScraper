'''
Author: Henry Yeomans
Created: 2021-01-27

A cli application for bho_scraper.
'''

import click
from bho_scraper.bho_scraper import BHOScraper

DEFAULT_DOWNLOAD = False

@click.command()
@click.argument("series")
@click.argument("queries")
@click.argument("path")
def scrape(series, queries, path):

    series  = [str(item) for item in series.strip('[]').split(',')]
    queries = [str(item) for item in queries.strip('[]').split(',')]
    scraper = BHOScraper()
    scraper.scrape_series(series, queries, path)
    # scraper = BHOScraper()
    # if type(series) == str:
    #     series = [series]
    # if type(queries) == str:
    #     queries = [queries]
  
    # with click.progressbar(series) as series_bar:
    #     for series_name in series_bar:
    #         click.echo("Scraping {}".format(series_name))
    #         with click.progressbar(queries) as queries_bar:
    #             for query in queries_bar:
    #                 scraper.scrape_series(series_queries=series_name, queries=query, path=path)
    click.echo("==================== SCRAPING COMPLETED ====================")
    click.echo("*.csv files saved to: {}".format(path))
    click.echo("============================================================")