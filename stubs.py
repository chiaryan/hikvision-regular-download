import os

def hikRequest(url, data):
  match url:
    case '/artemis/api/video/v1/cameras/playbackURLs':
      return {
        'url': 'asdf',
        'authentication': 'asdfa'
      }
    case '/artemis/api/video/v1/download':
      return {
        'downloadID': 'asdf'
      }
    case '/artemis/api/video/v1/downloadURL':
      return {
        'url': 'asdf'
      }

def downloadFromUrl(filename, url):
  bts = url.encode()
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'wb') as file:
    file.write(bts)
