from urllib.request import Request, urlopen

# Creates a web request object for the specified URL
def generateWebRequest(URL):
  return Request(URL, headers={
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
  })

# Returns the content of a website at the specified URL
def getURLContents(URL):
  try:
    return str(urlopen(generateWebRequest(URL)).read())
  except Exception as e:
    print(str(e))
