""" A bot to make the wordkeeper's job a little easier during games of Contact.

wordkeeper> !challenge @player1 @player2
slaskbot> @player1 @player2: type !ready when here
player1> !ready
player2> !ready
slaskbot> (wordkeeper) Starting countdown...
slaskbot> 3
slaskbot> 2
slaskbot> 1
slaskbot> go!

"""

import logging
import re
import time

import config
from models.contact import Challenge


# Number of seconds we wait for someone to be ready
TIMEOUT = 30


def on_message(msg, server):
    channel = server["channel"]

    with Challenge.lock(channel) as challenge:
        if re.search(r"!contactreset", msg.get("text", "")):
            challenge.reset(channel)
            return "contactbot reset"

        state = challenge.state
        if state == Challenge.COMPLETED:
            return start_challenge(challenge, msg)
        elif state == Challenge.WAITING_FOR_READY:
            return set_ready(challenge, msg)
        elif state > 0:
            return tick(challenge)
        else:
            challenge.reset()
            if config.DEBUG:
                log = logging.getLogger(__name__)
                log.warn("Channel %s has illegal state %d" % (channel, state))
            return "sorry guys jeff is not good with computer"


def start_challenge(challenge, msg):
    match = re.findall(r"!challenge (.*)", msg.get("text", ""))
    if not match:
        return

    players = [x.lower() for x in match[0].split() if valid_name(x)]
    if len(players) < 2:
        return "You need to tag all the people who contacted (at least two)"

    challenge.start_challenge(msg.get("user_name", ""))
    return "%s: type !ready when here" % (' '.join(players))


def valid_name(name):
    """True iff the name is a valid Slack username

    Slack's draconian naming conventions make it a little less likely
    that someone will bork the contactbot.

    """
    return all([c.isalnum() or c in '-_' for c in name])


def set_ready(challenge, msg):
    match = re.search(r"!ready")
    if not match:
        if int(time.time()) - challenge.time > TIMEOUT:
            challenge.reset()
            return "It's been too long since the last !ready. Giving up."
        else:
            return

    challenge.set_ready(msg.get("user_name", ""))

    if challenge.is_ready():
        challenge.start_clock()
        return "(%s) Starting countdown..." % (challenge.challenger)


def tick(challenge):
    dt = int(time.time()) - challenge.time

    if 0 <= dt <= 1:
        time.sleep(1 - dt)

    state = challenge.tick()
    if state != 0:
        return "%d..." % (state)
    else:
        return "go!"
