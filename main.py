from datetime import date, datetime, timedelta
from util import *
from retry import retry as trycall, HikApiTimeoutException
import backoffsequences
# from stubs import *

TIMEOUT = 8.0
INTERVAL = 0.5
CONFIG = readConfig()

def tryDownloadUrlEndpoint(downloadId: str) -> str:
  try:
    response = hikRequest('/artemis/api/video/v1/downloadURL', {
    'downloadID': downloadId
    })
  except HikApiException:
    raise HikApiTimeoutException

  if ('url' in response):
    return response['url']
  else:
    raise HikApiTimeoutException

def downloadByCameraId(cameraIndexCode: str, cameraName: str, beginInterval: datetime, endInterval: datetime):
  beginStr = beginInterval.isoformat()
  endStr = endInterval.isoformat()
  filename = f'video/{cameraIndexCode}/{beginInterval.date().isoformat()}/{beginInterval.isoformat().replace(":", "_")}.mp4'

  if os.path.exists(filename):
    print(f'{filename} exists, skipping')
    return

  try:
    response = hikRequest('/artemis/api/video/v1/cameras/playbackURLs', {
      'cameraIndexCode': cameraIndexCode,
      'recordType': '0',
      'protocol': 'rtsp',
      'beginTime': beginStr,
      'endTime': endStr,
    })
  except HikApiException:
    raise HikApiTimeoutException
  url, authentication = response['url'], response['authentication']
  
  try:
    response = hikRequest('/artemis/api/video/v1/download', {
      'url': url,
      'authentication': authentication,
      'beginTime': beginStr,
      'endTime': endStr,
      'videoType': 1
    })
  except HikApiException:
    raise HikApiTimeoutException
  downloadId = response['downloadID']
  
  try:
    downloadUrl = ""
    def tryDownload():
      nonlocal downloadUrl
      downloadUrl = tryDownloadUrlEndpoint(downloadId)
    
    trycall(tryDownload, backoffsequences.exponential(2, 0.5, 2, 20))
  except HikApiTimeoutException:
    raise(HikApiException(f'ran out of retries for /artemis/api/video/v1/download'))

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
        trycall(lambda: downloadByCameraId(cId, cName, beginInterval, endInterval), (1 for _ in range(3)))
      except HikApiTimeoutException as e:
        with open('error.log', 'a') as file:
          file.write(f'error downloading from camera {cName} from {beginInterval.isoformat()} to {endInterval.isoformat()}: {str(e)}\n')
