import psutil
from os import getpid

mypid = getpid()
for proce in psutil.process_iter():
      try:
           processName=proce.name()
           processID=proce.pid

           if "python" in processName and proce.pid!=mypid:
           		print(processName, ':::', processID)
           		proce.terminate()

      except Exception as e:
           print(str(e))