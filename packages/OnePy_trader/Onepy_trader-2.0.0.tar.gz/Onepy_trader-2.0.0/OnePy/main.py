import queue

from OnePy.config import CUSTOM_MODULE, EVENT_LOOP, SYS_MODEL, SYS_MODULE
from OnePy.environment import Environment
from OnePy.event import Event
from OnePy.sys_module.components.logger import BacktestLogger
from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.components.order_checker import PendingOrderChecker
from OnePy.sys_module.components.output import OutPut
from OnePy.variables import GlobalVariables


class OnePiece(object):

    env = Environment()

    def __init__(self):
        self.market_maker = MarketMaker()
        self.order_checker = PendingOrderChecker()
        self.cur_event = None
        self.env.logger = BacktestLogger()

    def sunny(self, summary=True):
        """主循环，OnePy的核心"""
        """TODO: 写test保证event的order正确"""
        self._initialize_trading_system()

        while True:
            try:
                self.cur_event = self.env.event_bus.get()
            except queue.Empty:
                if self.market_maker.update_market():
                    self.order_checker.run()
                else:
                    self.output.summary() if summary else None

                    break
            else:
                self._run_event_loop()

    def _run_event_loop(self):
        for element in self.env.event_loop:
            if self._event_is_executed(**element):
                break

    def _event_is_executed(self, if_event, then_event, module_dict):
        if self.cur_event.event_type == if_event:
            [value.run() for value in module_dict.values()]
            self.env.event_bus.put(Event(then_event)) if then_event else None

            return True

    def _initialize_trading_system(self):
        self.env.refresh()

        for module in SYS_MODULE+CUSTOM_MODULE+SYS_MODEL:
            module.env = self.env
        self.env.gvar = GlobalVariables()
        self.env.event_loop = EVENT_LOOP
        self.market_maker.initialize()
        self._custom_initialize()

        if self.env.recorder:
            self.env.recorder.initialize()

    def _custom_initialize(self, *funcs):
        for func in funcs:
            func()

    @property
    def output(self):
        return OutPut()

    @property
    def logger(self):
        return self.env.logger
