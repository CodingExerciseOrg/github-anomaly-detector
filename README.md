# GitHub Anomaly Detector

A command-line application that receives GitHub organization webhook events and
alerts on suspicious behavior.

## Suspicious behaviors detected

| # | Behavior | GitHub event |
|---|----------|--------------|
| 1 | Code pushed between **14:00–16:00 ET** | `push` |
| 2 | Team created with the prefix **"hacker"** (case does not matter) | `team` |
| 3 | Repository **deleted within 10 minutes** of creation | `repository` |

ET means EST(Winter)/EDT(Summer) Time (America/New_York Time Zone) 

If restricted time window includes midnight (00:00 / 12:00 AM), add two time windows into config file. 

For example, 22:00-23:59 and 00:00-02:00. All times are in America/New_York timezone  

## Requirements

- Python 3.10+
- A GitHub organization with webhook access
- [smee.io](https://smee.io) (or ngrok) for local webhook tunnelling. You do not need to use smee if your webhook server has public IP and does not have NAT issues.


## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
npm install --global smee-client        # tool to forward smee events
```


### 2. Set up smee.io (only if you test the program locally or your server is behind NUT)

1. Go to https://smee.io and click **Start a new channel**.
2. Copy your unique smee URL (e.g. `https://smee.io/xxxxxxxxx`).
3. In a separate terminal, start the forwarder:

```bash
smee --url https://smee.io/xxxxxxxxx --target http://localhost:5125/webhook
```


### 3. Register the webhook on your GitHub organization

1. Go to your org → **Settings → Webhooks → Add webhook**.
2. Set **Payload URL** to your smee URL.
3. Set **Content type** to `application/json`.
4. Set a **Secret** — make it a system environment variable called WEBHOOK_SECRET
5. Under *"Which events?"* choose **Send me everything** (or select individual events).
6. Click **Add webhook**.

To set environment variables for windows, run:
```bash
$env:WEBHOOK_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

To set them for Linux, run:
```bash
export WEBHOOK_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 4. Run the app (locally or on the server)

```bash
# Basic
python main.py
```

You should see:
```
INFO - Starting GitHub anomaly detector on port 5125
```

When a suspicious event occurs, an alert is printed to the console:

```
============================================================
  SUSPICIOUS ACTIVITY DETECTED
============================================================
  Title      : Code pushed during restricted window (14:00–16:00)
  Event Type : push
  Detected At: 2024-06-01 14:32:11 EDT
  Details:
    - pusher: user_name
    - repository: my-org/my-repo
    - branch: refs/heads/main
    - push_time_ET: 14:32:11
    - matched_window: 14:00-16:00
    - commit_count: 3
============================================================
```

## Extending the system

### Adding a new detector

1. Create a file in `detectors/`, e.g. `detectors/my_detector.py`.
2. Subclass `BaseDetector`, set `github_event_types`, implement `analyze()`.
3. Register it in `main.py`:

```python
from detectors.my_detector import MyDetector
dispatcher.register_detector(MyDetector())
```

### Adding a new notifier

1. Create a file in `notifiers/`, e.g. `notifiers/slack_notifier.py`.
2. Subclass `BaseNotifier`, implement `notify()`.
3. Register it in `main.py`:

```python
from notifiers.slack_notifier import SlackNotifier
dispatcher.register_notifier(SlackNotifier(webhook_url="..."))
```

There is a built-in email notifier called email_notifier.py. You must use an email application password for the sender email,as 
well as input a reciever email. DO NOT USE your main Google or Yahoo account password. You can input your own sender and destination emails in config.json, and the application password should be an environment variable.

For Windows, use:
```bash
$env:EMAIL_APPLICATION_PASSWORD = "xxxxxxxxxxxxxxxx" 
```

For Linux, use:
```bash
export EMAIL_APPLICATION_PASSWORD = "xxxxxxxxxxxxxxxx"
```

The email notifier currently tested and works for google and yahoo email addresses as sender. If using a google sender, use "smtp.mail.yahoo.com" for the smtp_host. If using google, 
use "smtp.google.com" in config.json.