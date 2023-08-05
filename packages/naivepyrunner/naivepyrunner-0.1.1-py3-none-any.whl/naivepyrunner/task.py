from time import time

class Task(object):
    def __init__(self, task, duetime):
        self.task = task
        self.duetime = duetime
        self.execution_times = []
        self.average_execution_time = 0
        self.probable_delay = 0

    def execute(self):
        start = time()
        sleep_time = self.task.execute()
        self.duetime = sleep_time + time()
        self.probable_delay = 0

        # update execution time
        ex_time = time()-start
        if len(self.execution_times) > 7:
            self.execution_times.pop(0)
        self.execution_times.append(ex_time)
        self.average_execution_time = (sum(self.execution_times)
            / len(self.execution_times))

        return sleep_time >= 0
