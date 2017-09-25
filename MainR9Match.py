'''
Created on 2017年9月11日

@author: T450S
'''

import signal
import get_config
import file_lock
import r9_ul_dl_match
'''
@readfile   port
@todo      unknow 
'''
def get_user_cfg():
    
    cfg=get_config.loadCfgFile()
    if cfg == None:
        print('cfg file load error')
        return False
    else:
        return True

def app():
    cfg=get_config.loadCfgFile()
    if cfg == None:
        print('cfg file load error')
    ss=r9_ul_dl_match.R9UlDlMatch(cfg)
    print('start proc')
    ss.run()    
if __name__ == "__main__":
    file_lock.app_lock(app,'MainR9Match')