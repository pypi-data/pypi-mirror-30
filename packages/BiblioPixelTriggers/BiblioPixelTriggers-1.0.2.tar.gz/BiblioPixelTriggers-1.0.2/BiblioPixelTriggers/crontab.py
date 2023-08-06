from datetime import datetime
from croniter import croniter
import time
import sys

try:
    from bibliopixel.remote import trigger
except ImportError:
    from bibliopixel.animation.remote import trigger


class crontab(trigger.TriggerBase):
    def __init__(self, q, events, **kwargs):
        super().__init__(q, events)
        self.crontabs = []
        for event in self.events:
            tab = croniter(event['config'], datetime.now())
            self.crontabs.append({
                'name': event['name'],
                'tab': tab,
                'next': tab.get_next(datetime)
            })

    def start(self):
        while True:
            now = datetime.now().replace(second=0, microsecond=0, tzinfo=None)
            for c in self.crontabs:
                if c['next'] == now:
                    self.trigger(c['name'])
                    c['next'] = c['tab'].get_next(datetime)
            time.sleep(60 - datetime.now().second)


sys.modules[__name__] = crontab
