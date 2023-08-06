import arrow

from OnePy.environment import Environment
from OnePy.event import EVENT, Event


class MarketMaker(object):

    env = Environment

    def update_market(self):
        try:
            self._update_bar()
            self._check_todate()
            self._update_recorder()
            self.env.event_bus.put(Event(EVENT.Market_updated))

            return True
        except StopIteration:
            self._update_recorder(final=True)

            return False

    def initialize(self):
        self.initialize_feeds()
        self.initialize_cleaners()

    def initialize_feeds(self):
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: value.get_bar()})

    def initialize_cleaners(self):
        for value in self.env.cleaners.values():
            value.initialize_buffer_data()

    def _update_recorder(self, final=False):
        for recorder in self.env.recorders.values():
            recorder.update(final)

    def _update_bar(self):
        for iter_bar in self.env.feeds.values():
            iter_bar.next()

    def _check_todate(self):
        if self.env.todate:
            if arrow.get(self.env.gvar.trading_datetime) > arrow.get(self.env.todate):
                raise StopIteration
