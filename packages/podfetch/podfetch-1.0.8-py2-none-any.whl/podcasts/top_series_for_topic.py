import json
from multiprocessing.dummy import Pool as ThreadPool
import requests
from podcasts.constants import ITUNES_GENRE_LOOKUP_URL, ITUNES_TOP_SERIES_URL

def read_url(url):
  response = requests.get(url)
  return json.loads(response.content)

def fetch_genres():
  tuples = [] # will have entries of type (id:int, name:string)
  data = read_url(ITUNES_GENRE_LOOKUP_URL)
  genres = data['26']['subgenres']
  for genre in genres.values():
    tuples.append((int(genre['id']), str(genre['name'])))
    if 'subgenres' in genre:
      for subgenre in genre['subgenres'].values():
        tuples.append((int(subgenre['id']), str(subgenre['name'])))
  return tuples

def fetch_top_series(genre=None):
  # The genre `None` indicates top series for all genres
  if genre is None:
    url = ITUNES_TOP_SERIES_URL.format('')
  else:
    url = ITUNES_TOP_SERIES_URL.format('/genre=' + str(genre))
  data = read_url(url)
  series_ids = [
      int(entry['id']['attributes']['im:id']) for entry in data['feed']['entry']
  ]
  return genre, series_ids

def fetch_series_all_genres(num_threads=10):
  genre_tuples = fetch_genres()
  genre_ids = [gid for (gid, _) in genre_tuples]
  genre_ids.append(None)
  pool = ThreadPool(num_threads)
  results = pool.map(fetch_top_series, genre_ids)
  pool.close()
  pool.join()
  return results
