===========
bho_scraper
===========


A simple web scraper designed to collect references to words or phrases in documents contained in the British History Online catalogue.

Description
===========

Usage
=====
- Command Line:
``scrape "[<series_a>, <series_b>,...]" "[<query_a>, <query_b>,...]" <path_to_save_destination>``

- Code:
``from bho_scraper import BHOScraper``

``scraper = BHOScraper()``

``scraper.scrape([<series_a>, <series_b>,...], [<query_a>, <query_b>,...], <path_to_save_destination> (OPTIONAL)])``


To-do
=====
- Search for best match to series and add "did you mean ...?"
- Improve CLI argument input
- Unit test for cli
- Unit test for various exceptions.
