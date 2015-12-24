'''
Requires Python 2.7 and Paramiko to be installed.
This using RSA based key authentication to log into our JunOS device.
We've also imported the StringIO library to assist us.
One of the new and exciting things this does is establish a connection to 
a remote host, then continues on to another host. 
One of the assumptions here is that RSA key local to the box initiating the conenction
is the same one used at the far end host.
'''

import paramiko
import time
import StringIO
import socket



bastion_host = '192.168.1.125'
far_end_host = '192.168.13.2'
user = 'dave'
passw = 'super-secret-password'



#We'll need to set up a local port to listen to.
#Otherwise we won't be able to capture in the incomming traffic.

def make_socket(listen_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_ip, 0))
    return sock

sock = make_socket('127.0.0.1')

#And set them up in a the following vars:
local_listen_ip, local_listen_port = sock.getsockname()



#Read the contents of the private key file and store it.
private_key_file = open('/Users/dave/.ssh/git_id_rsa', 'r')
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
#to host '192.168.1.125' , then continues on to log in using the same key to host '192.168.13.2'
#Hopefully this is clear, if we can't establish a connection, we'll set "chan" to false.
#This is useful in determining if we should even bother moving on to other activities . 
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(bastion_host, username=user, pkey=decrypted_key)
    #This is new, I'll need a transport object from the bastion/jump box to create the new session
    #to the destination.
    transport = ssh.get_transport()
    channel = transport.open_channel("direct-tcpip", (far_end_host,22),(local_listen_ip, local_listen_port))
    #Great, now letting Paramiko know to perform SSH Agent forwarding on this transport object.
    forward = paramiko.agent.AgentRequestHandler(transport.open_session())
    #Finally, we can then attempt to connect to the far end host.
    ssh2 = paramiko.SSHClient()
    ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #You'll notice that this is slightly different from the the initial conenction.
    #We simply supply the host, username, and add the channel that we'll be forwarding.
    ssh2.connect(far_end_host, username=user,sock=channel)
    #Our remote shell will now be to the far end device.
    chan = ssh2.invoke_shell()
except:
    print "Login to %s failed" % (far_end_host,)
    chan = False


if chan:
    resp = issue_command(chan, "show version|no-more", 2)
    ssh2.close()
    ssh.close()
    print resp
else:
    print "Sorry, there is no connection to the host %s" % (far_end_host,)
