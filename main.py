from datetime import date, datetime, timedelta
from util import *
from time import sleep
# from stubs import *

TIMEOUT = 8.0
INTERVAL = 0.5

class HikApiTimeoutException(HikApiException):
  pass

def retrydownloadUrl(downloadId: str):
  t = 0.0
  while t <= TIMEOUT:
    response = hikRequest('/artemis/api/video/v1/downloadURL', {
    'downloadID': downloadId
    })
    if ('url' in response):
      return response['url']
    sleep(INTERVAL)
    t += INTERVAL
  raise HikApiTimeoutException

def downloadByCameraId(cameraIndexCode: str, beginInterval: datetime, endInterval: datetime):
  beginStr = beginInterval.isoformat()
  endStr = endInterval.isoformat()
  response = hikRequest('/artemis/api/video/v1/cameras/playbackURLs', {
    'cameraIndexCode': cameraIndexCode,
    'recordType': '0',
    'protocol': 'rtsp',
    'beginTime': beginStr,
    'endTime': endStr,
  })

  url, authentication = response['url'], response['authentication']

  response = hikRequest('/artemis/api/video/v1/download', {
    'url': url,
    'authentication': authentication,
    'beginTime': beginStr,
    'endTime': endStr,
    'videoType': 1
  })
  downloadId = response['downloadID']

  downloadUrl = None
  try:
    downloadUrl = retrydownloadUrl(downloadId)
  except HikApiTimeoutException:
    raise(HikApiException(f'ran out of retries'))

  filename = f'video/{cameraIndexCode}/{beginInterval.date().isoformat()}/{beginInterval.isoformat().replace(":", "_")}.mp4'

  downloadFromUrl(filename, downloadUrl.replace(':9016:443', ''))

BEGIN_TIME, END_TIME, CAMERA_IDS = readConfig()['BEGIN_TIME'], readConfig()['END_TIME'], readConfig()['CAMERA_IDS'] 
if 'DATES' in readConfig():
  DATES = readConfig()['DATES']
else:
  DATE = date.today()
  if DATE.isoweekday() - 1 not in readConfig()['WEEKDAYS']:
    print('not today exiting')
    exit(0)
  else:
    DATES = [DATE]

for DATE in DATES:
  BEGIN_DATETIME, END_DATETIME = [datetime.combine(DATE, t) for t in (BEGIN_TIME, END_TIME)]
  for cid in CAMERA_IDS:
    for (beginInterval, endInterval) in iterDate(BEGIN_DATETIME, END_DATETIME, timedelta(minutes=1)):
      try:
        downloadByCameraId(cid, beginInterval, endInterval)
      except (HikApiException, requests.exceptions.ConnectionError) as e:
        with open('error.log', 'a') as file:
          file.write(f'error downloading from camera {cid} from {beginInterval.isoformat()} to {endInterval.isoformat()}: {str(e)}\n')
