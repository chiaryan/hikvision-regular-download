import requests
import json
import hmac
import hashlib
from base64 import b64encode
from datetime import time
from configparser import ConfigParser
import os

def readConfig(): 
  config = ConfigParser()
  config.read("config.ini")
  values = config['VALUES']

  return {
    'OPENAPI_DOMAIN': values['domain'],
    'USER_ID': values['userId'],
    'USER_SECRET': values['secret'],
    'BEGIN_TIME': time.fromisoformat(values['beginTime']),
    'END_TIME': time.fromisoformat(values['endTime']),
    'CAMERA_IDS': values['cameras'].split(',')
  }

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

def hikRequest(endpoint, data = {}):
  url = f"{OPENAPI_DOMAIN}{endpoint}"
  payload = json.dumps(data)

  signatureString = f'''POST
*/*
application/json
x-ca-key:{USER_ID}
{endpoint}'''
  signature = generateSignature(signatureString, USER_SECRET)

  headers = {
    'X-Ca-Key': USER_ID,
    'X-Ca-Signature-Headers': 'X-Ca-Key',
    'X-Ca-Signature': signature,
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  return response.json()['data']

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
  bts = requests.request('GET', url, verify=False).content
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'wb') as file:
    file.write(bts)

