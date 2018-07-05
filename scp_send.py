import sys
import paramiko
import time
class scp():
    def __init__(self,remote_ip,remote_port,username,password):
        self._rip = remote_ip
        self._port = remote_port
        self._sftp = None
        self._t = None
        self._username = username
        self._passwodr = password
        
        self._connect()
    def _connect(self):
        while True:
            try:
                self._t.close()
            except:
                pass
            try:
                self._t = paramiko.Transport((self._rip,self._port))
                self._t.connect(username=self._username, password=self._passwodr)  # 登录远程服务器
                self._sftp = paramiko.SFTPClient.from_transport(self._t)   # sftp传输协议
                print('[info] -> connect success!')
                break
            except:
                print('[error] -> connect failed!')
                time.sleep(1)
    def _callback(self,a,b):
        pass
#         sys.stdout.write('%s Data Transmission %10d [%3.2f%%]\n' %(time.ctime(),a,a*100./int(b)))
#         sys.stdout.flush()
    def scp_get(self,remote_path,local_path):
        src = remote_path 
        des = local_path
        while True:
            try:
                self._sftp.get(src,des)
                break
            except:
                print('[error] ->scp_get')
                self._connect()
                self._sftp.get(src,des)
    def scp_attr(self,content):
#         return self._sftp.listdir_attr(content)
        while True:
            try:
                return self._sftp.listdir_attr(content)
    #             break
            except:
                print('[error] ->scp_attr')
                self._connect()
                return self._sftp.listdir_attr(content)
    def scp_list_dir(self,path='.'):
        while True:   
            try:     
                return self._sftp.listdir(path)
            except:
                print('[error] ->scp_list_dir')
                self._connect()
                return self._sftp.listdir(path)
    def scp_rm_file(self,file):
        self._sftp.remove(file)
    def scp_mkdir(self,content):
#         print(content)
        while True:
            try:     
                self._sftp.mkdir(content)
                break 
            except:
                print('[error] ->scp_mkdir')
                self._connect()
                self._sftp.mkdir(content)
    def scp_put(self,remote_path,local_path):
        src = remote_path 
        des = local_path
        while True:
            try:
                self._sftp.put(des,src,callback=self._callback)
                break
            except:
                print('[error] ->scp_put')
                self._connect()
                self._sftp.put(des,src,callback=self._callback)
#         print(self._sftp.listdir_attr('./DLFILE/')[0].st_mtime)
#         print(self._sftp.listdir_attr('./DLFILE/')[0].st_atime)
if __name__ == "__main__":
    #remote_scp_put('127.0.0.1','DLFILE/commit.txt','commit.txt','cyp','cao1991')
    fl=scp('127.0.0.1',18990,'cyp','cao1991')
    # test reconncet
    while True:
        fl.scp_put('DLFILE/commit.txt','commit.txt')
        fl.scp_get('DLFILE/commit.txt','a.txt')
        time.sleep(1)
