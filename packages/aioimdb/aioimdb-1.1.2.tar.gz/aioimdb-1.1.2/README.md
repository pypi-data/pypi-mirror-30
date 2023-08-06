# aioimdb (IMDb + Python 3.6 + Asyncio)

[![Build Status](https://travis-ci.org/fpierfed/aioimdb.png?branch=master)](https://travis-ci.org/fpierfed/aioimdb)

Python asyncio IMDb client using the IMDb JSON web service made available for their iOS app. This version requires Python 3.6 or later. It is based off of the [synchronous version by Richard O'Dwyer](https://github.com/richardARPANET/imdb-pie).

## API Terminology

- `Title` this can be a movie, tv show, video, documentary etc.
- `Name` this can be a credit, cast member, any person generally.

## Installation

To install aioimdb, simply:
```bash
pip install aioimdb
```

## How To Use

### Initialise The Client
```python
from aioimdb import Imdb
async with Imdb() as imdb
    result = await imdb.<method call>    # <-- see Available Methods below
```

Example:
```python
from aioimdb import Imdb
async with Imdb() as imdb
    result = await imdb.get_title('tt0111161')
```


### Available Methods

NOTE: For each client method, if the resource cannot be found they will raise `LookupError`, if there is an API error then `ImdbAPIError` will raise.

Example | Description
--------- | ---------
`await get_title('tt0111161')` | Returns a dict containing title information
`await search_for_title("The Dark Knight")` | Returns a dict of results
`await search_for_name("Christian Bale)` | Returns a dict of results
`await title_exits('tt0111161')` | Returns True if exists otherwise False
`await get_title_genres('tt0303461')` | Returns a dict containing title genres information
`await get_title_credits('tt0303461')` | Returns a dict containing title credits information
`await get_title_quotes('tt0303461')` | Returns a dict containing title quotes information
`await get_title_ratings('tt0303461')` | Returns a dict containing title ratings information
`await get_title_connections('tt0303461')` | Returns a dict containing title connections information
`await get_title_similarities('tt0303461')` | Returns a dict containing title similarities information
`await get_title_videos('tt0303461')` | Returns a dict containing title videos information
`await get_title_news('tt0303461')` | Returns a dict containing news
`await get_title_trivia('tt0303461')` | Returns a dict containing trivia
`await get_title_soundtracks('tt0303461')` | Returns a dict containing soundtracks information
`await get_title_goofs('tt0303461')` | Returns a dict containing "goofs" and teaser information
`await get_title_technical('tt0303461')` | Returns a dict containing technical information
`await get_title_companies('tt0303461')` | Returns a dict containing information about companies related to title
`await get_title_episodes('tt0303461')` | Returns a dict containing season and episodes information
`await get_title_episodes_detailed(imdb_id='tt0303461', season=1)` | Returns a dict containing detailed season episodes information
`await get_title_top_crew('tt0303461')` | Returns a dict containing detailed information about title's top crew (ie: directors, writters, etc.)
`await get_title_plot('tt0111161')` | Returns a dict containing title plot information
`await get_title_plot_synopsis('tt0111161')` | Returns a dict containing title plot synopsis information
`await get_title_awards('tt0111161')` |Returns a dict containing title plot information
`await get_title_releases('tt0111161')` | Returns a dict containing releases information
`await get_title_versions('tt0111161')` | Returns a dict containing versions information (meaning different versions of this title for different regions, or different versions for DVD vs Cinema)
`await get_title_user_reviews('tt0111161')` | Returns a dict containing user review information
`await get_title_metacritic_reviews('tt0111161')` | Returns a dict containing metacritic review information
`await get_title_images('tt0111161')` | Returns a dict containing title images information
`await get_name('nm0000151')` | Returns a dict containing person/name information
`await get_name_filmography('nm0000151')` | Returns a dict containing person/name filmography information
`await get_name_images('nm0000032')` | Returns a dict containing person/name images information
`await get_name_videos('nm0000032')` | Returns a dict containing person/name videos information
`validate_imdb_id('tt0111161')` | Raises `ValueError` if not valid 
`await get_popular_titles()` | Returns a dict containing popular titles information
`await get_popular_shows()` | Returns a dict containing popular tv shows
`await get_popular_movies()` | Returns a dict containing popular movies 


## Requirements

    1. Python 3.6 or later
    2. See requirements.txt


## Running The Tests

```bash
pip install -r test_requirements.txt
py.test tests
```
