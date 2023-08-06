# ImdbPie (Python 3.6 + Asyncio Version)

[![PyPI](https://img.shields.io/pypi/v/aioimdb.svg)](https://pypi.python.org/pypi/aioimdb)
[![Python Versions](https://img.shields.io/pypi/pyversions/aioimdb.svg)](https://pypi.python.org/pypi/aioimdb)
[![Build Status](https://travis-ci.org/fpierfed/aioimdb.png?branch=master)](https://travis-ci.org/fpierfed/aioimdb)

Python asyncio IMDB client using the IMDB json web service made available for their iOS app. This version requires Python 3.6 or later. It is based off of the [synchronous version by Richard O'Dwyer](https://github.com/richardARPANET/imdb-pie).

## API Terminology

- `Title` this can be a movie, tv show, video, documentary etc.
- `Name` this can be a credit, cast member, any person generally.

## Installation

To install aioimdb, simply:
```bash
pip install git+https://github.com/fpierfed/aioimdb.git
```

## How To Use

### Initialise the client
```python
from aioimdb import Imdb
async with Imdb() as imdb
    ... [your code here]
```

### Available methods

NOTE: For each client method, if the resource cannot be found they will raise `LookupError`, if there is an API error then `ImdbAPIError` will raise.

#### get_title

```python
async with Imdb() as imdb:
    await imdb.get_title('tt0111161')
    # Returns a dict containing title information
```

#### get_title_genres

```python
async with Imdb() as imdb:
    await imdb.get_title_genres('tt0303461')
    # Returns a dict containing title genres information
```

#### get_title_credits

```python
async with Imdb() as imdb:
    await imdb.get_title_credits('tt0303461')
    # Returns a dict containing title credits information
```

#### get_title_quotes

```python
async with Imdb() as imdb:
    await imdb.get_title_quotes('tt0303461')
    # Returns a dict containing title quotes information
```

#### get_title_ratings

```python
async with Imdb() as imdb:
    await imdb.get_title_ratings('tt0303461')
    # Returns a dict containing title ratings information
```

#### get_title_connections

```python
async with Imdb() as imdb:
    await imdb.get_title_connections('tt0303461')
    # Returns a dict containing title connections information
```

#### get_title_similarities

```python
async with Imdb() as imdb:
    await imdb.get_title_similarities('tt0303461')
    # Returns a dict containing title similarities information
```

#### get_title_videos

```python
async with Imdb() as imdb:
    await imdb.get_title_videos('tt0303461')
    # Returns a dict containing title videos information
```

#### get_title_episodes

```python
async with Imdb() as imdb:
    await imdb.get_title_episodes('tt0303461')
    # Returns a dict containing season and episodes information
```

#### get_title_plot

```python
async with Imdb() as imdb:
    await imdb.get_title_plot('tt0111161')
    # Returns a dict containing title plot information
```

#### get_title_plot_synopsis

```python
async with Imdb() as imdb:
    await imdb.get_title_plot_synopsis('tt0111161')
    # Returns a dict containing title plot synopsis information
```

#### get_title_awards

```python
async with Imdb() as imdb:
    await imdb.get_title_awards('tt0111161')
    # Returns a dict containing title awards information
```

#### get_title_releases

```python
async with Imdb() as imdb:
    await imdb.get_title_releases('tt0111161')
    # Returns a dict containing releases information
```

#### get_title_versions

```python
async with Imdb() as imdb:
    await imdb.get_title_versions('tt0111161')
    # Returns a dict containing versions information (meaning different versions of this title for different regions, or different versions for DVD vs Cinema)
```

#### get_title_user_reviews

```python
async with Imdb() as imdb:
    await imdb.get_title_user_reviews('tt0111161')
    # Returns a dict containing user review information
```

#### get_title_metacritic_reviews

```python
async with Imdb() as imdb:
    await imdb.get_title_metacritic_reviews('tt0111161')
    # Returns a dict containing metacritic review information
```

#### get_title_images

```python
async with Imdb() as imdb:
    await imdb.get_title_images('tt0111161')
    # Returns a dict containing title images information
```

#### title_exists

```python
async with Imdb() as imdb:
    await imdb.title_exists('tt0111161')
    # Returns True if exists otherwise False
```

#### search_for_title
```python
async with Imdb() as imdb:
    await imdb.search_for_title("The Dark Knight")
    # Returns list of dict results
    [{'title': "The Dark Knight", 'year':  "2008", 'imdb_id': "tt0468569"},{'title' : "Batman Unmasked", ...}]
```

#### search_for_name
```python
async with Imdb() as imdb:
    await imdb.search_for_name("Christian Bale")
    # Returns list of dict results
    [{'imdb_id': 'nm0000288', 'name': 'Christian Bale'},{'imdb_id': 'nm7635250', ...}]
```

#### get_name

```python
async with Imdb() as imdb:
    await imdb.get_name('nm0000151')
    # Returns a dict containing person/name information
```

#### get_name_filmography

```python
async with Imdb() as imdb:
    await imdb.get_name_filmography('nm0000151')
    # Returns a dict containing person/name filmography information
```

#### get_name_images

```python
async with Imdb() as imdb:
    await imdb.get_name_images('nm0000032')
    # Returns a dict containing person/name images information
```

#### get_name_videos

```python
async with Imdb() as imdb:
    await imdb.get_name_videos('nm0000032')
    # Returns a dict containing person/name videos information
```

#### validate_imdb_id

```python
async with Imdb() as imdb:
    await imdb.validate_imdb_id('tt0111161')
    # Raises `ValueError` if not valid
```

#### get_popular_titles

```python
async with Imdb() as imdb:
    await imdb.get_popular_titles()
    # Returns a dict containing popular titles information
```

#### get_popular_shows

```python
async with Imdb() as imdb:
    await imdb.get_popular_shows()
    # Returns a dict containing popular titles information
```

#### get_popular_movies

```python
async with Imdb() as imdb:
    await imdb.get_popular_movies()
    # Returns a dict containing popular titles information
```

## Requirements

    1. Python 3.6 or later
    2. See requirements.txt

## Running the tests

```bash
pip install -r test_requirements.txt
py.test tests
```


