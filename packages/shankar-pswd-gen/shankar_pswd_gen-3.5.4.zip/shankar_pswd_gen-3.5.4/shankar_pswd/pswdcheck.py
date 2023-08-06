
def checkpswd(pswd):
    if len(pswd)>=8 and not pswd.islower()==True and not pswd.isupper()==True and not pswd.isnumeric()==True and not pswd.isalpha()==True and not pswd.isalnum==True:
        return "Strong Password"
    else:
        return "Weak Password"
    
    
     
        
        
    
