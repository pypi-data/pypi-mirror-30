import pathlib
import threading
import time


class LogFileObserver(threading.Thread):

    def __init__(self, log_path):
        threading.Thread.__init__(self)
        self.path = pathlib.Path(log_path)
        # This list will contain all the lines of the file
        self.lines = []
        # The actual file object
        self.file = self.path.open(mode='r')

        self.interval = 0.1

        self._callbacks = []

    def run(self):
        # self.read()
        self.tail()

    def add_callback(self, func):
        self._callbacks.append(func)

    def tail(self):
        try:
            while True:
                where = self.file.tell()
                line = self.file.readline()
                if not line:
                    time.sleep(self.interval)
                    self.file.seek(where)
                else:
                    self.lines.append(line)
                    # Calling the callbacks with the line as argument
                    for callback in self._callbacks:
                        callback(line)
        finally:
            self.file.close()

    def read(self):
        with self.path.open(mode='r') as file:
            self.lines = file.readlines()
            print(self.lines)


if __name__ == '__main__':
    l = LogFileObserver('/home/jonas/test')
    l.start()

    with open('/home/jonas/test', mode='w+') as file:
        while True:
            file.write('hallo\n')
            file.flush()
            time.sleep(1)