import random
from random import shuffle
#pswd= list(map(chr, range(33, 127)))
#shuffle(pswd)

def generate(leng):
        
        pswd= list(map(chr, range(33, 127)))   
        lst=[]
        for i in range(leng):
                shuffle(pswd)
                a=random.randint(0,93)
                t=pswd[a]
                lst.append(t)


        fp=''.join(lst)
        return fp

     
	

     
	



