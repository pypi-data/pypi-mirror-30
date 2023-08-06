import time, math

from urllib.parse import quote

from .web import getURLContents
from .scraper import get_all_imgage_urls_from_html, download_images
from .utility import create_sub_directory

def scrapeImages( search_queries='nicolas cage', limit=5, sub_dir_name='<query-string>', output_directory='downloads', delay=0 ):

  search_queries = search_queries if isinstance(search_queries, list) else [str(item) for item in search_queries.split(',')]
  sub_dir_name = str(sub_dir_name)
  output_directory = str(output_directory)

  t0 = time.time()
  errorCount = 0
  imgIndex = 0

  for i in range(len(search_queries)):

    search_query = search_queries[i]

    ''' SCRAPE URLS '''
    print("\n Query no.: " + str(imgIndex + i + 1) + " -->" + '"' + str(search_query) + '"')
    print("Scraping...")

    # set for further filtering; color, size, etc
    params = ''

    url = 'https://www.google.com/search?q='
    url += quote(search_query)
    url += '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch'
    url += params
    url += '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

    raw_html = getURLContents(url)
    time.sleep(0.1)
    imgURLs = get_all_imgage_urls_from_html(raw_html, limit=limit)

    print("Total Image URLs: " + str(len(imgURLs)))

    t1 = time.time()
    total_time = t1 - t0

    print("Total time taken: " + str(math.floor(total_time)) + " Seconds")


    ''' DOWNLOAD URLS '''
    print("\n Downloading...")

    dir_name = search_query if sub_dir_name == '<query-string>' else sub_dir_name

    # make a new directory for this search_query
    create_sub_directory(dir_name, output_directory)


    errorCount += download_images( imgURLs, output_directory + "/" + dir_name, delay=delay, start_index=imgIndex )

    if dir_name != '<query-string>': imgIndex += len(imgURLs)

  print("\n Everything downloaded!")
  print("Total Errors: " + str(errorCount) + "\n")
