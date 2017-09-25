'''
Created on 2017年3月2日

@author: T450S
'''
import logging  
import logging.config  
  
logging.config.fileConfig('log.conf')  
root_logger = logging.getLogger('root')  
root_logger.debug('test root logger...')  
  
logger = logging.getLogger('main')  
logger.info('test main logger')  
logger.info('start import module \'mod\'...')  

smtploger = logging.getLogger('smtp') 
smtploger.info('test main logger')  
smtploger.info('start import module \'mod\'...')  

