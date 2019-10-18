from pexpect import pxssh
import re, time

class ssh2pc():
    def __init__(self,host,username,password):
        self.host = host
        self.username = username
        self.password = password
        self.sshkey = "/Users/khanhlh/stagging"
        
        self.spawn = pxssh.pxssh()
        #initial ssh-login session:
        self.sshKeyLogin()

    def sshPasswordLogin(self):
        if not self.spawn.login (self.host, self.username, self.password):
            print ("####SSH session failed on password-login: " + self.host)
            print (str(self.spawn))
            return False
        else:
            print ("\n####SSH session password-login successful: " + self.host + "\n")    
            return True
    
    def sshKeyLogin(self):
        if not self.spawn.login (self.host, self.username, ssh_key=self.sshkey):
            print ("####SSH session failed on sshkey-login: " + self.host)
            print (str(self.spawn))
            return False
        else:
            print ("\n####SSH session sshkey-login successful: " + self.host + "\n")
            return True

    def logout(self):
        self.spawn.logout()
        print ("\n####SSH session logout successful: " + self.host + "\n")

    def grepPid(self, stakename):
        #Grep process id of file run.sh
        self.spawn.sendline('sudo ps aux | grep ' + stakename)
        self.spawn.prompt()         
        res_pid = self.spawn.before.decode('UTF-8')
        print(res_pid) 

        #Get list of process id
        pid_list = []
        res_listpid = res_pid.split("\n")
        for pid in res_listpid:
            get_pid = re.search(r"^\w+\s+(\d+)\s", pid)
            if get_pid:
                pid_list.append(get_pid.group(1))
        
        #1 default pid is the grep color, so, the pid list must be larger than 1. 
        if len(pid_list) > 1:
            return pid_list
        else:
            #pid list length = 1, return false (no pid found)
            return False

    def killPort(self, port):
        self.spawn.sendline ('sudo netstat -nltp | grep ' + port)
        self.spawn.prompt()         # match the prompt
        
        getpid = re.search(r"LISTEN\s+(\d+)", self.spawn.before.decode('UTF-8'))
        if getpid:
            self.spawn.sendline ('sudo kill -9 ' + getpid.group(1))
            self.spawn.prompt()
            print (self.spawn.before.decode('UTF-8'))
        else:
            print("cant kill the pid on port " + port)
    
    def stopDocker(self, stakename):
        #Step1: kill run_stakename.sh
        #Get list of process id
        pid_list = self.grepPid(stakename)
        if pid_list:
            for pid in pid_list:
                self.spawn.sendline ('sudo kill -9 ' + pid)
                self.spawn.prompt()
                print(self.spawn.before.decode('UTF-8'))
        else:
            print("WARNING: no pid found for " + stakename)

        #Step2: stop docker container
        #Send docker ps
        self.spawn.sendline('sudo docker ps')
        self.spawn.prompt() 
        res_dockerps = self.spawn.before.decode('UTF-8')
        print(res_dockerps)

        #Get docker container name
        get_dockername = re.search(r"\s+(\w*" + stakename + ")", res_dockerps)
        if get_dockername:
            #stop docker container
            self.spawn.sendline ('sudo docker stop ' + get_dockername.group(1))
            self.spawn.prompt()
            print(self.spawn.before.decode('UTF-8'))
            return True
        else:
            print("ERROR: cant stop the docker container: " + stakename)
            return False

    def startDocker(self, stakename):
        #Step1: kill file run_stakename.sh
        #Grep process id of file run.sh
        pid_list = self.grepPid(stakename)
        if pid_list:
            for pid in pid_list:
                self.spawn.sendline ('sudo kill -9 ' + pid)
                self.spawn.prompt()
                print(self.spawn.before.decode('UTF-8'))
        else:
            print("WARNING: no pid found for " + stakename)

        #Step2: List file in current directory (for debuging purpose)
        self.spawn.sendline ('ll')
        self.spawn.prompt()
        print(self.spawn.before.decode('UTF-8'))

        #Step3: Execute file run_stakename.sh 
        self.spawn.sendline ('sudo bash run_' + stakename + '.sh')
        self.spawn.prompt() 
        res_bash = self.spawn.before.decode('UTF-8')
        print(res_bash)
        #If file run_stakename.sh not found, then may be file name is stakename.sh
        if re.search("No such file or directory",res_bash):
            self.spawn.sendline ('sudo bash ' + stakename + '.sh')
            self.spawn.prompt() 
            print(self.spawn.before.decode('UTF-8'))

        #Step4: Verfiy that .sh file is running
        pid_list = self.grepPid(stakename)
        if pid_list:
            print("INFO: " + stakename + ".sh is running")
        else:
            print("ERROR: no pid found for " + stakename)
            return False
        #Step5: Verify Docker container is running 
        print("INFO: wait for docker container up, sleep 5 sec")
        time.sleep(5)
        self.spawn.sendline ('sudo docker ps | grep ' + stakename)
        self.spawn.prompt() 
        res_bash = self.spawn.before.decode('UTF-8')
        print(res_bash)
        if re.search(stakename,res_bash):
            print("INFO: Docker container is up")
            return True
        else:
            print("ERROR: Docker container is NOT up")
            return False

    def deleteDatabase(self, stakename):
        #Step1: go to staking data-folder
        self.spawn.sendline ('cd data_' + stakename )
        self.spawn.prompt()
        if re.search("No such file or directory",self.spawn.before.decode('UTF-8')):
            self.spawn.sendline ('cd data/' + stakename )
            self.spawn.prompt()
            if re.search("No such file or directory",self.spawn.before.decode('UTF-8')):
                print("ERROR: Cant find the data folder")
                return False
        
        #Step2: delete everything in data-folder
        self.spawn.sendline ('ll')
        self.spawn.prompt()      
        print(self.spawn.before.decode('UTF-8'))
        if re.search("testnet",self.spawn.before.decode('UTF-8')):  
            self.spawn.sendline ('sudo rm -rfv *')
            self.spawn.prompt()        
            print(self.spawn.before.decode('UTF-8')) 
            return True
        else:
            print("ERROR: cant find testnet folder")
            return False
