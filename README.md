# discord bot

## Installation

```bash
python -m venv /path/to/env
pip install -r requirements.txt
```

## Environment variables

| Variable                            | Description                                                                                    |
|-------------------------------------|------------------------------------------------------------------------------------------------|
| `DISCORD_TOKEN`                     | Discord bot token                                                                              |
| `CHANNEL_ID_ANNOUNCEMENTS`          | The channel ID where the approved announcements are posted                                     |
| `CHANNEL_ID_ANNOUNCEMENTS_NEW`      | The channel ID where the new announcements are posted                                          | 
| `CHANNEL_ID_ANNOUNCEMENTS_VALIDATE` | The channel ID where the announcements are posted as Embed and the validators can approve them | 
| `ROLE_ID_ANNOUNCEMENT_VALIDATORS`   | The role ID of the validators who will get the announcements to approve                        |

## Usage

```bash
python main.py
```

Run `deactivate` to exit the virtual environment.
