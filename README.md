### Setup

requires a `config.ini` in the root, under `[VALUES]` section:

- `domain`
- `userId`: HCP generated
- `secret`: HCP generated
- `beginTime`: ISO 8601 standard
- `endTime`: ISO 8601 standard
- `cameras`comma-separated IDs of cameras

```ini
[VALUES]
domain = http://127.0.0.1:9016
userId = 12345678
secret = secretsecretsecretsecret
beginTime = 15:00:00+08:00
endTime = 15:10:00+08:00
cameras = 1,2,3
```