from time import sleep, time
from threading import Thread
from collections import deque

from .task import Task

class Pipeline(Thread):
    def __init__(self, task_list=None, async=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.walking = False
        self.tasks = deque()
        self.finished_tasks = task_list
        self.task_count = 0 # faster than len()
        self.expected_duration = 0
        self.probable_delay = 0
        self._delays = []
        self._task_hash = "";
        self._delay_lock = False
        self.async = async

    def run(self):
        self.walking = True
        while self.walking:
            if not self.tasks:
                self.expected_duration += 0.05
                sleep(0.05)
                self.expected_duration -= 0.05

            self.step()

            if self.tasks:
                if time() - self.tasks[0].duetime <= 1:
                    continue
                self.expected_duration += 0.05
                sleep(0.05)
                self.expected_duration -= 0.05

    def step(self):
        if not self.tasks:
            return

        if self.tasks[0].duetime <= time():
            task = self.tasks.popleft()
            if self.async:
                Thread(target=self._execute, args=(task,)).start()
            else:
                self._execute(task)

    def push(self, task, position=-1):
        if not isinstance(task, Task):
            raise Exception('task is not a Task but a '+str(type(task)))

        if position < 0:
            task.probable_delay = (
                self._calc_probable_delay(self.tasks[-1], task)
                    if self.tasks
                    else 0
            )
            self.tasks.append(task)
        elif position == 0:
            self.tasks.appendleft(task)
        elif position >= self.task_count:
            self.tasks.append(task)
        else:
            self.tasks.insert(position, task)  # slower than append
        self.task_count += 1
        self.expected_duration += task.average_execution_time

    def optimal_position(self, task, includeDelay=True):
        # pretty ugly
        if not self.tasks:
            return (-1, 0)

        (delays, tasks) = self._update_delays()
        task_count = len(tasks)
        if not includeDelay:
            for i in range(1, task_count-1):
                if (tasks[i].duetime > task.duetime
                    and tasks[i-1].duetime <= task.duetime):
                    return (0, i)
            return (0, -1)

        # like what the fuck, but okay...
        for i in range(len(delays), task_count):
            delays.insert(0, 0)

        min_delay = (self._calc_probable_delay(tasks[-1], task, delays[-1])
            if task_count > 0 else 0)
        min_pos = -1
        prefix_delay = 0

        for i in range(0, task_count-1):
            prefix_delay += (0 if i == 0 else delays[i-1])
            new_del = (prefix_delay
                + self._calc_insertion_delay(task, tasks, delays, i-1)
            )
            if new_del <= min_delay:
                min_delay = new_del
                min_pos = i+1

        return (min_delay, min_pos) # delay, position

    def _update_delays(self):
        if self._delay_lock:
            while self._delay_lock:
                sleep(0.01)
            return (self._delays, self.tasks)

        self._delay_lock = True

        # check if update needed
        new_hash = ""
        tasks = self.tasks.copy()
        if len(tasks) > 0:
            new_hash += str(id(tasks[0]))+";"
            new_hash += str(id(tasks[-1]))+";"
        new_hash += str(len(tasks))

        if new_hash == self._task_hash:
            self._delay_lock = False
            return (delays, tasks)

        self._delays[:] = [] if len(tasks) == 0 else [0]
        probable_delay = 0
        for i in range(0, len(tasks)-1):
            delay = self._calc_probable_delay(
                tasks[i], tasks[i+1], self._delays[i]
            )
            probable_delay += delay
            self._delays.append(delay)
        self.probable_delay = probable_delay
        self._delay_lock = False
        return (self._delays, tasks)

    def _calc_insertion_delay(self, task, task_list, delays, start=0):
        delay = 0
        if start >= 0:
            delay = self._calc_probable_delay(
                task_list[start],
                task,
                delays[start]
            )
        if len(task_list) > start+1:
            last_delay = self._calc_probable_delay(
                    task,
                    task_list[start+1],
                    delay
            )
            delay += last_delay
            for i in range(start+1, len(task_list)-1, 1):
                last_delay = self._calc_probable_delay(
                    task_list[i],
                    task_list[i+1],
                    last_delay
                )
                delay += last_delay
        return delay

    def _calc_probable_delay(self, prev, task, prev_delay=0, adjustments=0):
        return max(
            prev.duetime
                + prev_delay
                + prev.average_execution_time
                + adjustments
                - task.duetime,
            0
        )

    def _execute(self, task):
        dur = task.average_execution_time
        keep_alive = task.execute()
        self.task_count -= 1
        self.expected_duration -= dur
        if keep_alive:
            if self.finished_tasks is not None:
                self.finished_tasks.appendleft(task)
            else:
                self.tasks.append(task)
