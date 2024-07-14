from datetime import date, datetime, timedelta
from util import *
from time import sleep
# from stubs import *

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

  # some time later...
  sleep(5)

  response = hikRequest('/artemis/api/video/v1/downloadURL', {
    'downloadID': downloadId
  })
  downloadUrl = None
  try:
    downloadUrl = response['url']
  except KeyError:
    raise(f'could not download url for {beginInterval.isoformat()} to {endInterval.isoformat()}')

  filename = f'video/{cameraIndexCode}/{beginInterval.date().isoformat()}/{beginInterval.isoformat().replace(":", "_")}.mp4'

  downloadFromUrl(filename, downloadUrl.replace(':9016:443', ''))

BEGIN_TIME, END_TIME, CAMERA_IDS = readConfig()['BEGIN_TIME'], readConfig()['END_TIME'], readConfig()['CAMERA_IDS'] 

TODAY = date.today()
BEGIN_DATETIME, END_DATETIME = [datetime.combine(TODAY, t) for t in (BEGIN_TIME, END_TIME)]

for cid in CAMERA_IDS:
  for (beginInterval, endInterval) in iterDate(BEGIN_DATETIME, END_DATETIME, timedelta(minutes=1)):
    try:
      downloadByCameraId(cid, beginInterval, endInterval)
    except Exception as e:
      with open('error.log', 'a') as file:
        file.write(e)