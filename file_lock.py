'''
Created on 2017年3月6日

@author: T450S
'''

import win32event, pywintypes, win32api,sys

ERROR_ALREADY_EXISTS = 183 

def app_lock(app,appname):
    hmutex = win32event.CreateMutex(None, pywintypes.FALSE,appname) 
    if (win32api.GetLastError() == ERROR_ALREADY_EXISTS): 
        print('正在运行，按任意键结束运行')
        input()
        sys.exit(0) 
    else:
        app()
        
    
