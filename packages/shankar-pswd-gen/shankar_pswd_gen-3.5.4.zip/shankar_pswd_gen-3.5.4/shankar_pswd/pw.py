import random
from random import shuffle
pswd= list(map(chr, range(33, 127)))
shuffle(pswd)
print("Enter Length of password")
le=input(">>>")
leng=int(le)

for i in range(leng):
    

	a=random.randint(0,93)
	shuffle(pswd)
	t=pswd[a]
	print(t,end='')
print("")	
z=input("Press any key to continue......")


