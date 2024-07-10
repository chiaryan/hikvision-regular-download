from datetime import date, datetime, timedelta
from util import *

def downloadByCameraId(cameraIndexCode, beginInterval, endInterval):
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
    'endTime': endStr
  })
  downloadId = response['downloadID']

  # some time later...

  response = hikRequest('/artemis/api/video/v1/downloadURL', {
    'downloadID': downloadId
  })
  downloadUrl = response['url']

  downloadFromUrl(beginInterval, downloadUrl)

BEGIN_TIME, END_TIME, CAMERA_IDS = readConfig()['BEGIN_TIME'], readConfig()['END_TIME'], readConfig()['CAMERA_IDS'] 

TODAY = date.today()
BEGIN_DATETIME, END_DATETIME = [datetime.combine(TODAY, t) for t in (BEGIN_TIME, END_TIME)]

for cid in CAMERA_IDS:
  for (beginInterval, endInterval) in iterDate(BEGIN_DATETIME, END_DATETIME, timedelta(minutes=1)):
    downloadByCameraId(cid, beginInterval, endInterval)