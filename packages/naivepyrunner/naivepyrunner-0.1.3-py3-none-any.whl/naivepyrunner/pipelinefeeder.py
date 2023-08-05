from threading import Thread
from time import sleep

from .pipeline import Pipeline

class PipelineFeeder(Thread):
    def __init__(self, runner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner = runner
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            if not self.runner.tasks:
                sleep(0.05)
                continue
            self.feed()

    def feed(self):
        if not self.runner.tasks:
            return

        task = self.runner.tasks.pop()
        if self.runner.unlimited:
            pipe = Pipeline(async=False)
            pipe.push(task)
            if self.runner.running:
                pipe.start()
            self.runner.pipes.append(pipe)

        else:
            (pipe_no, pos) = self._calc_pipeno(task)
            self.runner.pipes[pipe_no].push(task, pos)

    def stop(self):
        self.running = False

    def _calc_pipeno(self, task):
        if self.runner.thread_count == 0 or self.runner.thread_count == 1:
            return (0, -1)

        min_index = 0
        (min_delay, min_pos) = self.runner.pipes[0].optimal_position(
            task, includeDelay=not self.runner.async_execution
        )
        for i in range(1, self.runner.thread_count):
            (delay, pos) = self.runner.pipes[i].optimal_position(
                task, includeDelay=not self.runner.async_execution
            )

            if (delay < min_delay
                or (delay == min_delay
                    and (self.runner.pipes[i].task_count
                            < self.runner.pipes[min_index].task_count)
                )
            ):
                min_delay = delay
                min_pos = pos
                min_index = i

        return (min_index, min_pos)
