from random import shuffle
import time
import platform
import os

ti=time.ctime()
ti=ti.replace(' ','')
ti=ti.replace(':','')

seed1=list(ti)
shuffle(seed1)

ar=platform.architecture()
ar=''.join(ar)

seed2=list(ar)
shuffle(seed2)

os1=os.getlogin()

seed3=list(os1)
shuffle(seed3)

p1=platform.python_compiler()
p1=p1.replace(' ','')

seed4=list(p1)
shuffle(seed4)

bu=platform.python_build()
bu=''.join(bu)
bu=bu.replace(' ','')

seed5=list(bu)
shuffle(seed5)

nd=platform.node()

seed6=list(nd)
shuffle(seed6)

pr=platform.processor()
pr=pr.replace(' ','')

seed7=list(pr)
shuffle(seed7)

rev=platform.python_revision()

seed8=list(rev)
shuffle(seed8)

plat=platform.system()
rel=platform.release()
ver=platform.version()
pyb=platform.python_branch()
oo=plat+rel+ver+pyb
oo=oo.replace(' ','')

seed9=list(oo)
shuffle(seed9)

pid=os.getpid()

seed10=list(pid)
shuffle(pid)



























