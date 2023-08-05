from time import sleep, time
from collections import deque

from .handler import Handler
from .task import Task
from .pipeline import Pipeline
from .pipelinefeeder import PipelineFeeder

class Runner(object):
    def __init__(self, handler_threads=-1, feeder_threads=1):
        if feeder_threads > handler_threads:
            feeder_threads = handler_threads
        self.pipes = []
        self.tasks = deque()
        self.unlimited = handler_threads < 0
        self.running = False;
        self.thread_count = handler_threads
        self.feeders = []

        for i in range(feeder_threads):
            feeder = PipelineFeeder(self)
            self.feeders.append(feeder)

        if not self.unlimited:
            for i in range(handler_threads):
                self.pipes.append(
                    Pipeline(self.tasks)
                )

    def add_handler(self, handler):
        if not isinstance(handler, Handler):
            raise Exception('handler is not a Handler but a '+str(type(handler)))
        task = Task(
            task = handler,
            duetime = time()
        )
        self.tasks.append(task)
        if self.unlimited:
            # feed it instantly
            PipelineFeeder(self).feed()

    def join(self):
        if self.running:
            self.stop()
        while self.pipes:
            self.pipes.pop().join()
        while self.feeder:
            self.feeder.pop().join()

    def start(self):
        self.run(blocking=False)

    def run(self, blocking=True):
        self.running = True
        for pipe in self.pipes:
            pipe.start()

        for feeder in self.feeders:
            feeder.start()

        if len(self.feeders) == 0:
            if self.thread_count == 0:
                # make everything in-place
                self._run_single()
            else:
                feeder = PipelineFeeder(self)
                if blocking:
                    feeder.run()
                else:
                    feeder.start()

    def stop():
        self.running = False
        for pipe in self.pipes:
            pipe.stop()
        for feeder in self.feeders:
            feeder.stop()

    def _run_single(self):
        pipe = Pipeline(self.tasks)
        def add_tasks():
            while self.tasks:
                task = self.tasks.pop()
                (_, pos) = pipe.optimal_position(task, includeDelay=False)
                pipe.push(task, pos)
        add_tasks()

        while self.running:
            task = pipe.step()
            self.tasks.clear()
            if task:
                (_, pos) = pipe.optimal_position(task, includeDelay=False)
                print('  ', task.task.hw, pos)
                pipe.push(task, pos)
            if not self.running:
                break
            add_tasks()
            if not self.tasks:
                sleep(0.01)
