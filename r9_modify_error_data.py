#!/usr/bin/env python3
'''
Created on 2018年3月26日

@author: T450S
'''

import os
whitelist = ['txt','wav']

def r9_get_ul_file():
    file_list = list()
    for parent,dirnames,filenames in os.walk('.'+os.sep):
        for filename in filenames:
            ext = filename.split('.')[-1]
            if ext in whitelist:
                    file_list.append(os.path.join(parent,filename))
    return file_list
def r9_modify_filename(fl):
    for name in fl:
        tmpfile=name.rsplit(os.sep,1)[-1]
        header = name.rsplit(os.sep,1)[0]
        if 't'==tmpfile[23] and '#' == tmpfile[35]:
            modifyname = tmpfile[:29]+'0'+tmpfile[32:]
            try:
                os.renames(name, header+os.sep+modifyname)
                print("%s -> %s"%(name,header+os.sep+modifyname))
            except:
                os.remove(name)
if __name__ == '__main__':
    fl = r9_get_ul_file()
    r9_modify_filename(fl)
