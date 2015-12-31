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


#Todo, make all of these arguments that can be passed to the script . 
#Also, the real value is to loop this through multiple far end devices and store the output somewhere.

bastion_host = "192.168.1.125" # Our 'bastion' or 'jump' box
far_end_host = "192.168.13.2" # The actual host we want to access
user = "dave" # Username , must match on bastion and destination host
passw = "super-secret-password" # Password for our encrypted RSA key
rsa_key_file = "/Users/dave/.ssh/id_rsa" #Path to the specific private key we need to access the destination host
command = "show version|no-more" #Command to issue at the far end host


#We'll need to set up a local port to listen to.
#Otherwise we won't be able to capture in the incomming traffic.
def make_socket(listen_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_ip, 0))
    return sock



#This function will take the local private key and decrypt it for use in our remote connections.
def decrypt_rsa_key(keyfile, password):
    #Read the contents of the private key file and store it.
    private_key_file = open(rsa_key_file, 'r')
    private_key = private_key_file.read()
    private_key_file.close()

    #Convert the contents of the private key into a string
    private_key_string = StringIO.StringIO(private_key)

    #Now, we need it decrypted in order to use it in Paramiko.
    #I've set a password on this private key so i'll need to supply the same password
    #in order to decrypt it. 
    decrypted_key = paramiko.RSAKey.from_private_key(private_key_string, password=passw)

    #Return the decrypted key string
    return decrypted_key


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

#Ok, lets open a local socket to receive data from the remote device. 
sock = make_socket('127.0.0.1')

#And grab the local ip and port we've just created and set them up in following vars:
local_listen_ip, local_listen_port = sock.getsockname()

#And now get the rsa key:
rsa_key = decrypt_rsa_key(rsa_key_file, passw)

#Sets up the ssh session and logs in as user "dave" using RSA based key authentication
#to host '192.168.1.125' , then continues on to log in using the same key to host '192.168.13.2'
#Hopefully this is clear, if we can't establish a connection, we'll set "chan" to false.
#This is useful in determining if we should even bother moving on to other activities . 
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(bastion_host, username=user, pkey=rsa_key)

    #This is new, I'll need a transport object from the bastion/jump box to create the a session
    #to the far end destination.
    transport = ssh.get_transport()
    channel = transport.open_channel("direct-tcpip", (far_end_host,22),(local_listen_ip, local_listen_port))

    #Great, now letting Paramiko know to perform SSH Agent forwarding on this transport object.
    #I do need to create an error handler to be sure connection to the bastion/jump box is established
    #before proceeding....
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

#If we're able to establish an ssh session to the remote device, we'll issue a command and capture the response.
#Otherwise, we'll just print some sort of error message.
if chan:
    resp = issue_command(chan, command, 2)
    ssh2.close()
    ssh.close()
    print resp
else:
    print "Sorry, there is no connection to the host %s" % (far_end_host,)
