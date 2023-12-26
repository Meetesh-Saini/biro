from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep


class Loader:
    def __init__(
        self,
        desc="Loading...",
        end="Done!",
        timeout=0.1,
        step_left="",
        step_right=" ",
    ):
        self.desc = desc
        self.end = end
        self.timeout = timeout
        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False
        self.step_left = step_left
        self.step_right = step_right

    def start(self):
        self._thread.start()

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(
                f"\r{self.step_left}{c}{self.step_right}{self.desc}",
                flush=True,
                end="",
            )
            sleep(self.timeout)

    def stop(self):
        self.done = True
        cols = get_terminal_size().columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}", flush=True)
