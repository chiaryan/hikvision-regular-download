### Setup

requires a `config.ini` in the root, under `[VALUES]` section:

- `domain`
- `userId`: HCP generated
- `secret`: HCP generated
- `beginTime`: ISO 8601 standard
- `endTime`: ISO 8601 standard
- `cameras`: comma-separated IDs of cameras
- (optional) `dates`: comma-separated dates in the format YYYY-MM-DD. When enabled, running `main.py` downloads from the specified date. Omit to use `date.today()`
- (optional) `days`: enabled days of the week. The script will fail to run on a disabled weekday. Omit to enable for all days

```ini
[VALUES]
domain = http://127.0.0.1:9016
userId = 12345678
secret = secretsecretsecretsecret
beginTime = 15:00:00+08:00
endTime = 15:10:00+08:00
cameras = 1,2,3
dates = 2022-01-01,2024-01-01
days = monday,thursday,Friday,Wednesday
```