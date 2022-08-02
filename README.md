# OwnTracks Http Server

This is python flask version of OwnTracks Server. Set the endpoint in app to `http://<your-host-ip>:<your-port>/pub` to report http events to your server.

## Features

1. Easy to use and easy to add your own process features.
2. No db dependency, only save to file.
3. A report api to show your region enter and leave.
4. Remove wrong ping-pang location.
5. Show time diff between each location change.


## How to run

```bash
pip install -r requirements.txt
python main.py
```
