import sys
import termcolor
import time
from threading import Thread

# def out_show():
    # tmp = ''
    # now_start_time = time.time()
    # while 1:
        # c = sys.stdin.read(1)

        # if c:
            # tmp += c
            # termcolor.cprint(c,"blue", end='')
        # if time.time() - now_start_time > 0.2:
            # termcolor.cprint(tmp,"blue", end='')
            # tmp = ''
        # elif "\n" in tmp:
            # termcolor.cprint(tmp,"blue", end='')
            # tmp = ''
            
    

# t = Thread(target=out_show)

# try:
    # t.start()
    # t.join()
# except (KeyboardInterrupt, Exception) as e:
    # pass
def Input():    
    for l in sys.stdin:
        # termcolor.cprint(l,"blue", end='')
        yield l.strip()