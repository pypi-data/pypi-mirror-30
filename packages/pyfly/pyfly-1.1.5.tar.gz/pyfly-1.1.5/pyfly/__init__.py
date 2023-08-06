from .core import task, TaskDataQueue, TaskSet, FlyQueen, async_task, sleep
from .runners import FlyMaster, FlySlave
from .events import task_success, task_fail 
try:
    from .web import WebApp
except:
    print("You should to install dash, if you want to run master on this pc!")

version = "1.1.5"