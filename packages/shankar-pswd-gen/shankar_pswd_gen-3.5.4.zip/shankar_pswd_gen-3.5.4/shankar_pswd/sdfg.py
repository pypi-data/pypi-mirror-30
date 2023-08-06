import time
st=time.time()
print("Start Time:"+str(st))
for i in range(500000000):
    a=i*i*i
    a=a*a
    

endt=time.time()
s=endt-st
print("End Time:"+str(endt))
print("Total Time Taken:"+str(s))
print('')
print(str(a))
