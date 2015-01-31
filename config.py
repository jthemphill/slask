import os
import json

import constants

config = {
    "username": constants.DEFAULT_BOT_NAME,
    "icon": constants.DEFAULT_BOT_ICON,
}

def bool_config(name):
    return True if os.environ.get(name) == "True" else False

# These should be Slack IDs
CONTACT_CHANNELS = json.loads(os.environ.get("CONTACT_CHANNELS", "[]"))

# JSON of the format:
# '{"channel_name": constants.CHANNEL_MOD_ALL or ["mod_name",]}'
CHANNEL_MOD_MAP = json.loads(os.environ.get("CHANNEL_MOD_MAP", "{}"))

CHANNEL_MOD_OPT_IN = bool_config("CHANNEL_MOD_OPT_IN")
DATABASE_URL = os.environ.get("DATABASE_URL")
DEBUG = bool_config("DEBUG")
SLACK_CONF_TOKEN = os.environ.get("SLACK_CONF_TOKEN")
