'''
Requires Python 2.7 and Paramiko to be installed


'''

import paramiko
import time


#Sets up the ssh session and logs in as user "dave" with password "password"
#to host '192.168.1.22' . 
#Also added "look_for_keys=False" and "allow_agent=False". 
#Paramiko will attempt to use any keys on the local host initially, but will crash and burn
#if they aren't accepted. The switch I'm testing against isn't able to use key based auth.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.22', username='dave', password='password', look_for_keys=False, allow_agent=False)


#Creates a channel object, to overcome weirdness with cisco devices
chan = ssh.invoke_shell()

#Sends the 'enable' command to enter privilidged mode.
#Note the '\n' after the command, this is equivalent to pressing "Enter".
chan.send("enable\n")
time.sleep(1)
chan.recv(9999)

#Sends the password, in this case, it's "password"
#Also note that '\n' is there at the end, you should realize we need this after every command.
chan.send("password\n")
time.sleep(1)
chan.recv(9999)

#Disables paging by issuing the "terminal length 0" command.
#I've added '\n' after the command.
chan.send("terminal length 0\n")
time.sleep(1)
chan.recv(9999)

#In this case we want to see the configured vlans, and store the response.
chan.send("show vlan brief\n")
time.sleep(1)
resp = chan.recv(9999)

#Great! We have all that we need, lets close the connection
ssh.close()

#We should have received a contiguous string of characters. 
#Let's now split it apart into distinct lines

resp = resp.split('\n')

#Added as an example to print each line individually
for line in resp:
    print line
