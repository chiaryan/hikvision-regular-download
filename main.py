from datetime import date, datetime, timedelta
from util import *
from time import sleep
# from stubs import *

TIMEOUT = 8.0
INTERVAL = 0.5
CONFIG = readConfig()

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

def downloadByCameraId(cameraIndexCode: str, cameraName: str, beginInterval: datetime, endInterval: datetime):
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

  filename = f'video/{cameraName}/{beginInterval.date().isoformat()}/{beginInterval.isoformat().replace(":", "_")}.mp4'

  downloadFromUrl(filename, downloadUrl.replace(':9016:443', ''))

BEGIN_TIME, END_TIME = CONFIG['BEGIN_TIME'], CONFIG['END_TIME']
if 'DATES' in CONFIG:
  DATES = CONFIG['DATES']
else:
  DATE = date.today()
  if DATE.isoweekday() - 1 not in CONFIG['WEEKDAYS']:
    print('not today exiting')
    exit(0)
  else:
    DATES = [DATE]

if 'CAMERA_IDS' in CONFIG:
  CAMERA_IDS = CONFIG['CAMERA_IDS']
  CAMERA_NAMES = getCameraNamesFromIds(CAMERA_IDS)
elif 'CAMERA_NAMES' in CONFIG:
  CAMERA_NAMES = CONFIG['CAMERA_NAMES']
  CAMERA_IDS = getCameraIdsFromNames(CAMERA_NAMES)
else:
  assert False, "no 'CAMERA_NAMES' or 'CAMERA_IDS' property"

for DATE in DATES:
  BEGIN_DATETIME, END_DATETIME = [datetime.combine(DATE, t) for t in (BEGIN_TIME, END_TIME)]
  for cId, cName in zip(CAMERA_IDS, CAMERA_NAMES):
    for (beginInterval, endInterval) in iterDate(BEGIN_DATETIME, END_DATETIME, timedelta(minutes=1)):
      try:
        downloadByCameraId(cId, cName, beginInterval, endInterval)
      except (HikApiException, requests.exceptions.ConnectionError) as e:
        with open('error.log', 'a') as file:
          file.write(f'error downloading from camera {cName} from {beginInterval.isoformat()} to {endInterval.isoformat()}: {str(e)}\n')
