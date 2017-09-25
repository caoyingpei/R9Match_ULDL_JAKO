'''
Created on 2017年3月3日

@author: T450S
'''
import json

# bandDict={
#    1:'band1',
#    3:'band3', 
#    38:'band38',
#    39:'band39',
#    40:'band40',
#    41:'band41'
# }
def loadCfgFile():
    try:
        fp=open('configFile/conf.json')
    except:
        return None
    re=json.load(fp)
    fp.close()
    return re
# def getSysDict(dictIn):
#     return dictIn['sys_para'][0]
# if __name__ == '__main__':
#     cfg=loadCfgFile()
#     if cfg == None:
#         print('cfg file load error')
#     print(getSysDict(cfg))