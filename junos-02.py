'''
Requires Python 2.7 and Paramiko to be installed.
This using RSA based key authentication to log into our JunOS device.
We've also imported the StringIO library to assist us. 
'''

import paramiko
import time
import StringIO

host = '192.168.1.125'
user = 'dave'
passw = 'super_secret_password'


#Read the contents of the private key file and store it.
private_key_file = open('/home/dave/.ssh/id_rsa', 'r')
private_key = private_key_file.read()
private_key_file.close()

#Convert the contents of the private key into a string
private_key_string = StringIO.StringIO(private_key)

#Now, we need it decrypted in order to use it in Paramiko.
#I've set a password on this private key so i'll need to supply the same password
#in order to decrypt it. 
decrypted_key = paramiko.RSAKey.from_private_key(private_key_string, password=passw)


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

#Sets up the ssh session and logs in as user "dave" using RSA based key authentication
#to host '192.168.1.125' . 
#Hopefully this is clear, if we can't establish a connection, we'll set "chan" to false.
#This is useful in determining if we should even bother moving on to other activities . 
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, pkey=decrypted_key)
    chan = ssh.invoke_shell()
except:
    print "Login to %s failed" % (host,)
    chan = False


if chan:
    resp = issue_command(chan, "show version|no-more", 2)
    ssh.close()
    print resp
else:
    print "Sorry, there is no connection to the host %s" % (host,)
