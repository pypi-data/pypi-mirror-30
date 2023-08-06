#__init__.py for cpu Module
all = ["lol"]
from multiprocessing import cpu_count


cpucores = cpu_count()

def cores():
    print("Your CPU has %d core(s)" % cpucores)

