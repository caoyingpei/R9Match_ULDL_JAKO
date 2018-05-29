'''
Created on 2017年3月2日

@author: T450S
'''
import logging  
import logging.config  
  
logging.config.fileConfig('configFile/log.conf')  
root_logger = logging.getLogger('root')  
root_logger.debug('test root logger...')  
  
logger = logging.getLogger('main')  
logger.info('test main logger')  
logger.info('start import module \'mod\'...')  
logger.exception("Exception Logged")

smtploger = logging.getLogger('smtp') 
smtploger.info('test main logger')  
smtploger.info('start import module \'mod\'...')  

