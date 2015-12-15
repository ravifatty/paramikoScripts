import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.21', username='dave', password='password')
chan = ssh.invoke_shell()


chan.send("enable\n")
time.sleep(1)
#resp = chan.recv(9999)

#print resp 

chan.send("password\n")
time.sleep(1)
#resp = chan.recv(9999)

print resp

chan.send("terminal length 0\n")
time.sleep(1)
#resp = chan.recv(9999)

#print resp

chan.send("show vlan brief\n")
time.sleep(1)
resp = chan.recv(9999)

if "VLAN" in resp:
    print "yes" 
    for line in resp:
        if "active" in line:
            print line
