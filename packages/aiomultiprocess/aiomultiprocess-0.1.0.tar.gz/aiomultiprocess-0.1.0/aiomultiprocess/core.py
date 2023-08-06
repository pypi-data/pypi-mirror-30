# Copyright 2018 John Reese
# Licensed under the MIT license

import asyncio
import logging
import os

log = logging.getLogger(__name__)


class Worker:
    def __init__(self, tx_queue, rx_queue):
        self.loop = None
        self.pid = None
        self.tx = tx_queue
        self.rx = rx_queue

    async def run(self):
        log.debug(f'{self.pid}: run loop started')

    def start(self):
        try:
            self.pid = os.getpid()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            self.loop.run_until_complete(self.run())

        except BaseException:
            log.exception('worker process failed')


class Pool:
    def __init__(self):
        pass

    def apply(self, coro, *args):
        pass

    def map(self, coro, inputs):
        pass
