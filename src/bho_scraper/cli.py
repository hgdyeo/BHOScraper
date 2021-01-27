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

    click.echo("==================== SCRAPING COMPLETED ====================")
    click.echo("*.csv files saved to: {}".format(path))
    click.echo("============================================================")