'''
Requires Python 2.7 and Paramiko to be installed


'''

import paramiko
import time

host = '192.168.1.22'
user = 'dave'
passw = 'password'
enable_pass = 'password'

#Ok, so, I'm creating a function to just take a command and send it to the device.
#This reduces the amount of time I need to add in the "\n", sleep and clear the buffer.
#There is a default sleep time of 1 second, but I can always change it for something 
#that may need to sit for a bit longer.
def issue_command(channel, command, delay=1):
    chan = channel
    command_str = command + "\n"
    chan.send(command_str)
    time.sleep(delay)
    resp = chan.recv(99999)
    return resp

#Sets up the ssh session and logs in as user "dave" with password "password"
#to host '192.168.1.22' . 
#Also added "look_for_keys=False" and "allow_agent=False". 
#Paramiko will attempt to use any keys on the local host initially, but will crash and burn
#if they aren't accepted. The switch I'm testing against isn't able to use key based auth.
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=passw, look_for_keys=False, allow_agent=False)
    chan = ssh.invoke_shell()
except:
    print "Login to %s failed" % (host,)
    chan = False


if chan:
    issue_command(chan, "enable")
    issue_command(chan, enable_pass)
    issue_command(chan, "terminal length 0")
    resp = issue_command(chan, "show vlan brief", 2)
    print resp
else:
    print "Sorry, there is no connection to the host %s" % (host,)
