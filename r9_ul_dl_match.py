'''
Created on 2017年9月11日

@author: T450S
'''

import os
import shutil
import struct
import time
import json
import re
import datetime

from progressbar import  ETA, ProgressBar, SimpleProgress, AbsoluteETA
    
from ctypes import cdll
_sopen = cdll.msvcrt._sopen
_close = cdll.msvcrt._close
_SH_DENYRW = 0x10
class R9UlDlMatch():
    '''
    R9 上下行JAKO文件匹配
    2017-10-17 增加将 文件大小小于？KB的文件转存为 空文件但名字不能改成LU
    '''

    whitelist = ['jako']
    
    
    
    def __init__(self, cfg):
        '''
        @1 读取配置文件
        '''
        print(json.dumps(cfg,indent = 4))
        self.r9_ul_file_content = cfg['R9_UL_FILE_CONTENT']
        self.r9_dl_file_exit_flag = cfg['R9_DL_FILE_EXIT']
        
        
        if self.r9_dl_file_exit_flag == "TRUE":
            self.r9_dl_file_content = cfg['R9_DL_FILE_CONTENT']
        self.r9_result_file_content = cfg['R9_RESULT_FILE_CONTENT']
        self.r9_result_file_content_empty = cfg['R9_RESULT_FILE_CONTENT_EMPTY']
        '''
        @2 初始化参数
        '''
        self.r9_ul_dl_period  = cfg['R9_UL_DL_PERIOD']
        self.r9_match_how_many_min_ago  = cfg['R9_MATCH_HOW_MANY_MIN_AGO']
        self.r9_check_period  = cfg['R9_CHECK_PERIOD']
        self.r9_check_file_status_period  = cfg['R9_CHECK_FILE_STATUS_PERIOD']
        self.r9_rm_old_file_flag = cfg['R9_RM_OLD_FILE_FLAG']
        try:
            self.r9_change_file_loc_kb_thres = cfg['R9_CHANGE_FILE_LOC_KB_THRES']
        except:
            self.r9_change_file_loc_kb_thres = 0
        self.r9_result_file_content_bak  = cfg['R9_RESULT_FILE_CONTENT_BAK']
        self.r9_result_file_content_bak_empty = cfg['R9_RESULT_FILE_CONTENT_BAK_EMPTY']
        try:
            self.r9_r9_open_file_filter_flag = cfg['R9_OPEN_FILE_FILTER_FLAG']
            self.r9_r9_open_log_flag = cfg['R9_OPEN_LOG_FLAG']
        except:
            self.r9_r9_open_file_filter_flag = "FALSE"
            self.r9_r9_open_log_flag = "FALSE"
        self.ulfile_dict = {} 
        self.dlfile_dict = {} 
        
        self.total_list_len = 0
    def is_open(self,file_name):
        if not self.r9_r9_open_file_filter_flag=='TRUE':
            return False
        try:
            firstSize = os.path.getsize(file_name)
            time.sleep(0.01)
            secondSize = os.path.getsize(file_name)
            if firstSize == secondSize:
                return False
            else:
                return False
        except:
            return True
    def r9_get_ul_file(self):
        file_list = list()
        for parent,dirnames,filenames in os.walk(self.r9_ul_file_content):
            for filename in filenames:
                ext = filename.split('.')[-1]
                if ext in self.whitelist:
                    if self.is_open(os.path.join(parent,filename))==False  and self.r9_file_filter(os.path.join(parent,filename)) == True:
                        file_list.append(os.path.join(parent,filename))
        return file_list

    def r9_get_dl_file(self):
        file_list = list()
        for parent,dirnames,filenames in os.walk(self.r9_dl_file_content):
            for filename in filenames:
                ext = filename.split('.')[-1]
                if ext in self.whitelist:
                    if self.is_open(os.path.join(parent,filename))==False and self.r9_file_filter(os.path.join(parent,filename)) == True:
                        file_list.append(os.path.join(parent,filename))
        return file_list

    def r9_ullist_proc(self):
        for file in self.r9_ulfile_list:
            cut_file=file.rsplit('.',1)[0]
            tmpList = cut_file.split('#')
#             print(tmpList)
            key = str(int(tmpList[len(tmpList)-2])%128)+tmpList[len(tmpList)-3]
            if key in  self.ulfile_dict.keys():
                self.ulfile_dict[key].append(cut_file)
            else:
                self.ulfile_dict[key] =[cut_file] 
    def r9_progress_bar_init(self,maxValue):
        self._pre_index_=0
        self._max_value_=maxValue
        widgets = ['progress: ',SimpleProgress(),' | ' , ' | ', ETA(), ' | ', AbsoluteETA()]
        self.pbar = ProgressBar(widgets=widgets, maxval=maxValue).start()
        
    def r9_progress_bar_update(self,index):
        self.pbar.update(index)
        
    def r9_progress_bar_finish(self):
        self.pbar.finish()
        
    def r9_match_progress_bar_print(self,index):
        if (index - self._pre_index_)*100/self._max_value_ >1:
            self._pre_index_=index
            self.r9_progress_bar_update(index)   
        
    def r9_split(self,file):
        cut_file=file.rsplit('.',1)[0]
        return cut_file.split('#')
    
    def r9_dllist_proc(self):
        for file in self.r9_dlfile_list:
            cut_file=file.rsplit('.',1)[0]
            tmpList = cut_file.split('#')
            key = str(int(tmpList[len(tmpList)-2])%128)+tmpList[len(tmpList)-3]
            if key in  self.dlfile_dict.keys():
                self.dlfile_dict[key].append(cut_file)
            else:
                self.dlfile_dict[key] =[cut_file] 
                
    def r9_get_voice_file_total_framenum(self,file):
        total_framenum = 0
        fp = open(file,'rb')
        try:
            fp.read(32)
            while True:
                read_result = struct.unpack('B',fp.read(1))[0]
                # 第二个比特 为0 
                if read_result%4>1:
                    fp.read(26)
                total_framenum = total_framenum+1
        except:
            fp.close()
        return  total_framenum
        
    def r9_voice_merge(self,ulfile_Loc,dlfile_Loc,remoteefile_Loc,UlFrameNum,DlFrameNum):
        
        '''
        @语音格式
                        前32个字节是文件头部，没有具体意义。暂定：前4字节为字符串"jako"，后28字节填0
                        从第33个字节开始，是文件具体内容。第33个字节bit0表示上下行，0表示上行，1表示下行，bit1表示是否静音，0表示静音，1表示有声音。如果为静音，表示40ms的静音，无后续字节，如果有声音，之后连续26个byte表示40ms编码码流。
                        文件无结束标志。
                        如示例文件"示例.jako"表示40ms的下行静音和40ms的上行语音
        @设计策略
           @1 统计上行的帧号 与下行的相差范围，计算上下行头的位置，
           @2 统计上下行的总帧数，与头的位置一起统计尾巴的位置
        '''
        cnt = UlFrameNum - DlFrameNum

        if cnt > 0 :
            dlhead = 0 
            ulhead = cnt
        else:
            dlhead = -cnt 
            ulhead = 0    
        
        ultail =  ulhead+self.r9_get_voice_file_total_framenum(ulfile_Loc)//2
        dltail  = dlhead+self.r9_get_voice_file_total_framenum(dlfile_Loc)//2
        
        
        totol_frame_num = 0
        if dltail> ultail:
            totol_frame_num = dltail
        else:
            totol_frame_num = ultail
            
        
        fw = open(remoteefile_Loc,'wb')
        fu = open(ulfile_Loc,'rb')
        fd = open(dlfile_Loc,'rb')
        try:
            fd.read(32)
            fw.write(fu.read(32))
            for i in range(totol_frame_num):
                if i < dlhead or i>dltail-1:
                    fw.write(b'\x01')
                else:
                    read_byte = fd.read(1)
                    read_result = struct.unpack('B',read_byte)[0]
                    # 第二个比特 为0 
                    fw.write(read_byte)
                    if read_result%4>1:
                        fw.write(fd.read(26))
                        
                    read_byte = fd.read(1)
                    read_result = struct.unpack('B',read_byte)[0]
                    # 第二个比特 为0 
                    if read_result%4>1:
                        fd.read(26)   
                
                if i < ulhead or i>ultail-1:
                    fw.write(b'\x00')
                else:
                    read_byte = fu.read(1)
                    read_result = struct.unpack('B',read_byte)[0]
                    if read_result%4>1:
                        fu.read(26)
                    
                    read_byte = fu.read(1)
                    read_result = struct.unpack('B',read_byte)[0]
                    # 第二个比特 为0 
                    fw.write(read_byte)
                    if read_result%4>1:
                        fw.write(fu.read(26))
 
                        
        except:
            print('[ERROR :] FORMAT_ERROR %s %s'%(ulfile_Loc,dlfile_Loc))
        fw.close()
        fd.close()
        fu.close()
    def r9_ul_dl_file_match_proc(self,key):
        
        i=0
        while i< len(self.ulfile_dict[key]):
            j=0
            match_flag = 0
            while j < len(self.dlfile_dict[key]):
                ulfile= self.ulfile_dict[key][i]
                dlfile= self.dlfile_dict[key][j]
                ultmpList = self.r9_split(ulfile)
                dltmpList = self.r9_split(dlfile)
                UlFrameNum= int(ultmpList[-1])
                DlFrameNum= int(dltmpList[-1])
                if abs(UlFrameNum - DlFrameNum)>self.r9_ul_dl_period:
                    pass
                else:
                    tmpfile=ulfile.rsplit(os.sep)[-1]
                    
                    tep = tmpfile.split('#')
                    if 1==int(tep[len(tep)-2])//128:
                        remotfile = self.r9_result_file_content_empty+'\\'+tmpfile[0:len(tmpfile)-20]+'.txt'
                    else:
                        remotfile = self.r9_result_file_content+'\\'+tmpfile[0:len(tmpfile)-20]+'.jako'
                    
                    try:
                        remotfile=remotfile.replace('##','#N#') 
                    except:
                        pass
                    split_header=remotfile.rsplit('\\',1)
                    
                    
                    if 1==int(tep[len(tep)-2])//128:
                        replace_header= split_header[1].replace(split_header[1][0:3],'nlo')
                        path = split_header[0]
                        bak_path = self.r9_result_file_content_bak_empty + '\\'+self.r9_get_year_month_day()
                    else:
                        path = split_header[0]
                        bak_path = self.r9_result_file_content_bak + '\\'+self.r9_get_year_month_day()
                        
                        
                        
                    replace_header= split_header[1].replace(split_header[1][0:29],split_header[1][0:26]\
                                    +dlfile.rsplit('\\',1)[1][26:29])
                    
                    
                    
                    
#                     path = split_header[0]+'\\'+self.r9_get_year_month_day()
#                     if not os.path.exists(path):
#                         os.makedirs(path) 
#                     remotfile = path+'\\'+replace_header
                    

                    if not os.path.exists(path):
                        os.makedirs(path) 
                    if not os.path.exists(bak_path):
                        os.makedirs(bak_path) 
                    remotfile = path+'\\'+replace_header
                    remotfile_bak = bak_path+'\\'+replace_header 
 
                    
                                   
                    if self.r9_r9_open_log_flag == 'TRUE':
                        if os.path.exists(remotfile):
                            print('[WARNING] : {%s} is exsit'%remotfile)
                            pass
                        print('[MATCHED] :\n    ->%s \n    ->%s'%(ulfile+'.jako',dlfile+'.jako'))
                    self.r9_voice_merge(ulfile+'.jako',dlfile+'.jako',remotfile,UlFrameNum,DlFrameNum)
                    
                    if 1==int(tep[len(tep)-2])//128:
                        f=open(remotfile,'w')
                        f.close()
                    shutil.copy(remotfile,remotfile_bak)
                    if self.r9_rm_old_file_flag == 'TRUE':
                        os.remove(ulfile+'.jako')
                        os.remove(dlfile+'.jako')
                    match_flag =1 
                    break
                j=j+1
            if match_flag == 1:
                self.proc_count_len = self.proc_count_len+2
                self.r9_match_progress_bar_print(self.proc_count_len)
                self.ulfile_dict[key].remove(self.ulfile_dict[key][i])
                self.dlfile_dict[key].remove(self.dlfile_dict[key][j])
            else:
                i=i+1
                
         
    def r9_ul_dl_match(self):
        '''
        @匹配规则:
        @1 上下行 SB_MASK相同
        @2 上下行的随机值相同
        @3 上下行的帧号不超过R9_ULDL_PERIOD 
        '''
        for key in self.dlfile_dict.keys(): 
            if key in self.ulfile_dict.keys():
                self.r9_ul_dl_file_match_proc(key)
        self.r9_ul_file_save()
        self.r9_dl_file_save()
        self.ulfile_dict= {}
        self.dlfile_dict= {}
    def r9_file_filter(self,filfile):
        '''
        @过滤策略 
                         
        @1     获取文件的时间 如果时间 与当前时间相差超过2s则认为可以通过过滤
        
        @2     文件所包含的‘#’数目过滤
        '''

        file_time = os.path.getctime(filfile)
        now_time = time.time()
        if not now_time - file_time > self.r9_match_how_many_min_ago *60:
            return False  
        if  filfile.count('#') <8:
            print('[ERROR :] FILE_NAME FORMAT ERROR [%s]'%filfile)
            return False
        return True
         
    def r9_dl_file_save(self):
        '''
        @1 处理匹配的程序
        '''
        for key in self.dlfile_dict.keys():
            for i in range(len(self.dlfile_dict[key])):
                current_file_loc = self.dlfile_dict[key][i]+'.jako'
                tmpfile=self.dlfile_dict[key][i].rsplit(os.sep)[-1]
                file_size = os.path.getsize(current_file_loc)/1024
                
                tep = tmpfile.split('#')
                if 1==int(tep[len(tep)-2])//128 or file_size < self.r9_change_file_loc_kb_thres:
                    path = self.r9_result_file_content_empty 
                    if not os.path.exists(path):
                        os.makedirs(path) 
                    bak_path = self.r9_result_file_content_bak_empty + '\\' + self.r9_get_year_month_day()
                    if not os.path.exists(bak_path):
                        os.makedirs(bak_path)
                        
                    if file_size < self.r9_change_file_loc_kb_thres:
                        remotfile = 'n'+tmpfile[1:len(tmpfile)-20]+'.txt'
                    else:
                        remotfile = tmpfile[0:len(tmpfile)-20].replace(tmpfile[0:3],'nlo')+'.txt'
                    
                    
                else:
                    path = self.r9_result_file_content 
                    if not os.path.exists(path):
                        os.makedirs(path) 
                    bak_path = self.r9_result_file_content_bak + '\\' + self.r9_get_year_month_day()
                    if not os.path.exists(bak_path):
                        os.makedirs(bak_path)
                    remotfile = tmpfile[0:len(tmpfile)-20]+'.jako'
#                 remotfile = tmpfile[0:len(tmpfile)-20]+'.jako'
                try:
                    remotfile=remotfile.replace('##','#N#') 
                except:
                    pass

                
                
                r=re.compile('IMEISV_(.*?)\.')
                l=r.findall(remotfile)
                if len(l)>0:
                    remotfile=remotfile.replace(l[0],l[0]+'0')
                
                  
                remotfile_bak = bak_path+'\\'+remotfile
                remotfile = path+'\\'+remotfile
                if self.r9_r9_open_log_flag == 'TRUE':
                    print(current_file_loc)
                    print('->',remotfile)
                self.proc_count_len = self.proc_count_len+1
                self.r9_match_progress_bar_print(self.proc_count_len)
                

                                    
                if self.r9_rm_old_file_flag == 'TRUE' :
                    if 1==int(tep[len(tep)-2])//128 or file_size < self.r9_change_file_loc_kb_thres:
                        f=open(remotfile,'w')
                        f.close()
                        f=open(remotfile_bak,'w')
                        f.close()
                        os.remove(current_file_loc)
                    else:
                        shutil.copy(current_file_loc,remotfile)
                        shutil.move(current_file_loc,remotfile_bak)
                    
                else:
                    shutil.copy(current_file_loc,remotfile)
                    shutil.copy(current_file_loc,remotfile_bak)
    def r9_get_year_month_day(self):
        
        return '%04d%02d%02d'%(datetime.datetime.now().year,
                datetime.datetime.now().month,
                datetime.datetime.now().day)
    def r9_ul_file_save(self):
        '''
        @1 处理匹配的程序
        '''
        for key in self.ulfile_dict.keys():
            for i in range(len(self.ulfile_dict[key])):
                current_file_loc = self.ulfile_dict[key][i]+'.jako'
                tmpfile=self.ulfile_dict[key][i].rsplit(os.sep)[-1]
                
                
                file_size = os.path.getsize(current_file_loc)/1024
                
                
                tep = tmpfile.split('#')
                
                if 1==int(tep[len(tep)-2])//128 or file_size < self.r9_change_file_loc_kb_thres:
                    if file_size < self.r9_change_file_loc_kb_thres:
                        remotfile = self.r9_result_file_content_empty+'\\'+'n'+tmpfile[1:len(tmpfile)-20]+'.txt'
                    else:
                        remotfile = self.r9_result_file_content_empty+'\\'+tmpfile[0:len(tmpfile)-20].replace(tmpfile[0:3],'nlo')+'.txt'
 
                    
                
                else:
                    remotfile = self.r9_result_file_content+'\\'+tmpfile[0:len(tmpfile)-20]+'.jako'
                
                r=re.compile('#.*?#.*?#(.*?)#N#')
                l=r.findall(remotfile)
                remotfile = remotfile.replace('#'+l[0]+'#N#','#N#'+l[0]+'#')
                
                try:
                    remotfile=remotfile.replace('##','#N#') 
                except:
                    pass
                
                split_header=remotfile.rsplit('\\',1)
#                 replace_header= split_header[1].replace(split_header[1][0:29],split_header[1][0:26]+'800')
                replace_header = split_header[1]
                path = split_header[0]
                
                r=re.compile('IMEISV_(.*?)\.')
                l=r.findall(replace_header)
                
                
                if len(l)>0:
                    replace_header=replace_header.replace(l[0],l[0]+'0')
                    
                    
            
                if 1==int(tep[len(tep)-2])//128 or file_size < self.r9_change_file_loc_kb_thres:
                    bak_path = self.r9_result_file_content_bak_empty + '\\'+self.r9_get_year_month_day()
                else:
                    bak_path = self.r9_result_file_content_bak + '\\'+self.r9_get_year_month_day()
                
                if not os.path.exists(path):
                    os.makedirs(path) 
                if not os.path.exists(bak_path):
                    os.makedirs(bak_path) 
                remotfile = path+'\\'+replace_header
                remotfile_bak = bak_path+'\\'+replace_header
                if self.r9_r9_open_log_flag == 'TRUE':
                    print(current_file_loc)
                    print('->',remotfile)
                self.proc_count_len = self.proc_count_len+1
                self.r9_match_progress_bar_print(self.proc_count_len)  
                if self.r9_rm_old_file_flag == 'TRUE':
                    if 1==int(tep[len(tep)-2])//128 or file_size < self.r9_change_file_loc_kb_thres:
                        f=open(remotfile,'w')
                        f.close()
                        f=open(remotfile_bak,'w')
                        f.close()
                        os.remove(current_file_loc)
                    else:
                        shutil.copy(current_file_loc,remotfile)
                        shutil.move(current_file_loc,remotfile_bak)
                else:
                    shutil.copy(current_file_loc,remotfile)
                    shutil.copy(current_file_loc,remotfile_bak)
#         pass

    def run(self):
        while True:
            print('[INFO] : start match ul dl file')
            self.r9_ulfile_list=self.r9_get_ul_file()
#             print(self.r9_ulfile_list)
            
            
            self.r9_ullist_proc()
            
            '''
            @todo: 程序测试
            @todo: 上下行文件的过滤（暂时不考虑）
            '''
#             print(self.ulfile_dict)
            if self.r9_dl_file_exit_flag == "TRUE":
                self.r9_dlfile_list=self.r9_get_dl_file()
                
                self.total_list_len = len(self.r9_ulfile_list)+len(self.r9_dlfile_list)
                
                
                self.proc_count_len = 0
                self.r9_progress_bar_init(self.total_list_len)
                
                self.r9_dllist_proc()
                self.r9_ul_dl_match()
                self.r9_progress_bar_finish()
            else:
                self.r9_ul_file_save()
                self.ulfile_dict= {}
            
            time.sleep(self.r9_check_period)
