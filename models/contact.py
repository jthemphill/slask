import contextlib
import time

from core.citext import CIText
from core.db import db


class Challenge(db.Model):
    ## States
    WAITING_FOR_READY = -1
    COMPLETED = 0
    # A positive state indicates the number of seconds we will wait for
    # the challengers
    COUNTDOWN = 4 # gives us 3... 2... 1... go!

    id = db.Column(db.Integer(), primary_key=True)
    channel = db.Column(CIText(), unique=True)

    state = db.Column(db.Integer())
    time = db.Column(db.Integer())

    challenger = db.Column(CIText())
    challenged = db.Column(CIText())
    ready = db.column(CIText())


    def __init__(self, channel):
        self.channel = channel
        self.reset()


    def reset(self):
        self.state = Challenge.COMPLETED
        self.time = int(time.time())
        self.challenger = ''
        self.challenged = ''
        self.ready = ''


    def start(self, challenger, challenged):
        """Wait for the challenged players to ready up"""
        self.state = Challenge.WAITING_FOR_READY
        self.challenger = challenger
        self.challenged = ' '.join(challenged)
        self.ready = ''


    def set_ready(self, player):
        if player not in self.challenged:
            return

        ready = set(self.ready.split())
        ready.add(player)

        self.ready = ' '.join(ready)
        self.time = int(time.time())


    def is_ready(self):
        challenged = set(self.challenged.split())
        ready = set(self.ready.split())
        return len(ready.intersection(challenged)) >= 2


    def start_clock(self):
        self.state = Challenge.COUNTDOWN
        self.time = int(time.time())


    def tick(self):
        """Decrement the state if positive"""
        self.time = int(time.time())
        if self.state <= 0:
            return self.state

        self.state -= 1
        return self.state


    @staticmethod
    def get(channel):
        """Get the challenge for the given channel (read-only)"""

        challenge = db.session.query(Challenge).filter_by(
            channel=channel
        ).first()

        if not challenge:
            challenge = Challenge(channel)
            db.session.add(challenge)

        return challenge


    @staticmethod
    @contextlib.contextmanager
    def lock(channel):
        """Checkout the challenge for the given channel (for reading and writing)"""
        challenge = db.session.query(Challenge).filter_by(
            channel=channel
        ).with_lockmode('update').first()

        if not challenge:
            challenge = Challenge(channel)
            db.session.with_lockmode('update').add(challenge)

        yield challenge
        db.session.commit()


    def __repr__(self):
        return "%s: %s -> [%s] (state: %s, time: %d)" % (
            self.channel,
            self.challenger,
            self.challenged,
            self.state,
            self.time,
        )
