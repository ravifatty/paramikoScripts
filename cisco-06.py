'''
Requires Python 2.7 and Paramiko to be installed
This is essentiall the same as cisco-05.py, however, I'm parsing
a different kind output. 
This one takes input in the form of a csv file and performs a 
"show archive config differences"
on all the devices listed.

This command shows the difference between the running config and the saved
startup config. 

Not so much of an issue on a few devices, but if your reloading a bunch of them, 
it would help to know what changes will not be present once they get restarted!

I've added a parser for the output to nicely display the differences. 
The main section of the script will add the host information, so we know 
which output belongs to which host.

The file format is something like :

host,username,password,enable_password

e.g.

192.168.1.10,dave,ssh-password,enable-password
192.168.1.11,jim,pass-word,enable-pass

'''

import paramiko
import time

#I've hard coded the command to run and filename, but this can easily be turned into a prompt.
#There should also be something like an 'isfile' to verify that the file actually
#exists.
device_file = "cisco.txt"
command = "show archive config differences"


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

#So, this takes a csv file as input and adds each line to a device list. 
#This will create a list of devices with their associated credentials and 
#return them in a 'list of lists'. The csv file should have the ip address, 
#username, password and privileged-exec mode password on each line.
#Need to add some validation and error handling here. 
def credential_list(file):
    try:
        devices = []
        with open(file) as data:
            for line in data:
                line = line.strip()
                credential = line.split(",")
                devices.append(credential)
    except:
        print "Could not open %s ." % (file,)
        devices = False
    return devices


#This diff_parser will take the response from our 
#"show archive config differences" command and split it up into lines. 
#It will ommit the first couple lines, which basically echo the command, 
#as well as the last line, which is simple a command prompt.
def diff_parser(data):
    data = data.split("\r")
    for i in range(0,len(data)):
        data[i] = data[i].strip()
    for i in range(2,len(data)-1):
        print data[i]

#Great, lets get the device IP, username, password, and enable password from our CSV file.
hosts = credential_list(device_file)

#If we are able to get the values out of the file, lets start grabbing data!
if hosts:
    #We'll loop through all the devices and grab the data from each of them
    for i in range(0,len(hosts)):
        #Sets up the ssh session and logs in as user specified in the file.
        #The IP address should be the first value, SSH username the second, password the third. 
        #The 'enable' password should be the fourth value.
        #We'll wrap the SSH session into a 'try..except' block so that failure at one host won't
        #kill our loop.
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hosts[i][0], username=hosts[i][1], password=hosts[i][2], look_for_keys=False, allow_agent=False)
            chan = ssh.invoke_shell()
        except:
            print "Login to %s failed." % (hosts[i][0],)
            print hosts[i][0]
            chan = False
        #If we've been successful at logging in , we'll run our diff_parser function on the response.
        if chan:
            issue_command(chan, "enable")
            issue_command(chan, hosts[i][3])
            issue_command(chan, "terminal length 0")
            resp = issue_command(chan, command, 5)
            ssh.close()
            print "Showing configuration differences for host %s :" % (hosts[i][0],)
            diff_parser(resp)
        else:
            print "Sorry, there is no connection to the host %s ." % (hosts[i][0],)
else:
    print "Invalid file."
