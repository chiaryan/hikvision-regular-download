import requests
import hmac
import hashlib
from base64 import b64encode
from datetime import time, date
from configparser import ConfigParser, Error as ConfigParserError
import os
from time import strptime as parsetime

class InvalidWeekdayError(ConfigParserError):
  pass

class NoCameraListError(ConfigParserError):
  pass

class HikApiException(Exception):
  pass

def readConfig(): 
  config = ConfigParser()
  config.read("config.ini")
  values = config['VALUES']

  ret = {
    'OPENAPI_DOMAIN': values['domain'],
    'USER_ID': values['userId'],
    'USER_SECRET': values['secret'],
    'BEGIN_TIME': time.fromisoformat(values['beginTime']),
    'END_TIME': time.fromisoformat(values['endTime']),
    'WEEKDAYS': {parsetime(d, '%A').tm_wday for d in values['days'].split(',')} if 'days' in values else set(range(0, 7))
  }

  if 'dates' in values:
    ret['DATES'] = [date.fromisoformat(s) for s in values['dates'].split(',')]

  if 'cameraNames' in values:
    ret['CAMERA_NAMES'] = values['cameraNames'].split(',')
  elif 'cameraIds' in values:
    ret['CAMERA_IDS'] = values['cameraIds'].split(',')
  else:
    if 'cameras' not in values:
      raise NoCameraListError('no property cameraNames, cameraIds or cameras')
    ret['CAMERA_IDS'] = values['cameras'].split(',')
  
  return ret

OPENAPI_DOMAIN, USER_ID, USER_SECRET = readConfig()['OPENAPI_DOMAIN'], readConfig()['USER_ID'], readConfig()['USER_SECRET']

def iterDate(start, end, step): 
  ctr = start
  end = end
  while ctr < end:
    next = ctr + step
    yield (ctr, next)
    ctr = next

def generateSignature(message, secret): 
  bytes = hmac.new(
    key = secret.encode(),
    msg = message.encode(), 
    digestmod = hashlib.sha256).digest()
  return b64encode(bytes).decode()


def hikRequest(url, data):
  match url:
    case '/artemis/api/video/v1/cameras/playbackURLs':
      return {
        'url': f'playback URL for camera {data["cameraIndexCode"]}, {data["beginTime"]} to {data["endTime"]}',
        'authentication': 'auth'
      }
    case '/artemis/api/video/v1/download':
      return {
        'downloadID': f'downloadID for url {data["url"]}'
      }
    case '/artemis/api/video/v1/downloadURL':
      return {
        'url': f'url for downloadID {data["downloadID"]}'
      }
    case '/artemis/api/resource/v1/cameras':
      return {
        'list': [
          {
            'cameraName': 'a',
            'cameraIndexCode': '1'
          },
          # {
          #   'cameraName': 'c',
          #   'cameraIndexCode': '3'
          # },
          {
            'cameraName': 'b',
            'cameraIndexCode': '2'
          },
          {
            'cameraName': 'd',
            'cameraIndexCode': '4'
          }
        ]
      }
    case _:
      raise

def getCameraIds(names: list[str]):
  response = hikRequest('/artemis/api/resource/v1/cameras', {
    'pageNo': 1,
    'pageSize': 500,
    'bRecordSetting': 0
  })
  cameraInfos: list[dict[str, str]] = response['list']

  return [next(c for c in cameraInfos if c['cameraName'] == cn)['cameraIndexCode'] for cn in names]

def findCamera(cameraInfos: list[dict[str, str]], property: str, value: str) -> dict[str, str]:
  return next(c for c in cameraInfos if c[property] == value)

def getCameraIdsFromNames(names: list[str]) -> list[str]:
  response = hikRequest('/artemis/api/resource/v1/cameras', {
    'pageNo': 1,
    'pageSize': 500,
    'bRecordSetting': 0
  })
  cameraInfos: list[dict[str, str]] = response['list']

  return [findCamera(cameraInfos, 'cameraName', cn)['cameraIndexCode'] for cn in names]

def getCameraNamesFromIds(ids: list[str]) -> list[str]:
  response = hikRequest('/artemis/api/resource/v1/cameras', {
    'pageNo': 1,
    'pageSize': 500,
    'bRecordSetting': 0
  })
  cameraInfos: list[dict[str, str]] = response['list']

  return [findCamera(cameraInfos, 'cameraIndexCode', cid)['cameraName'] for cid in ids]

def downloadFromUrl(filename, url):
  bts = f"content of {url}".encode()
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'wb') as file:
    file.write(bts)
