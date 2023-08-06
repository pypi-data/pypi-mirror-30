#! python3
import pyautogui, sys
print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x)+ ' Y: ' + str(y)
        print(positionStr+'\n', end='',flush=True)
        #print('\b' * len(positionStr), end='', flush=True)
        sr=open('mc.txt','a')
        sr.write(positionStr+'\n')
except KeyboardInterrupt:
    print('\n')
    sr.close()
