# paramikoScripts

OK, 

I'm creating this because it took me far too long to google the 
individual bits and pieces needed to get Paramiko to perform something
as simple as log in to priviliged mode and issue a "show" command. 

Most of the examples I've seen, while written very well and functional, are
a bit cluttered with error handling. While this is important, it was a little
challenging to filter out the basic mechanism that was the heart of the script
from the error handling portion. 

Hopefully this will help someone new or strugling. 

All of them will assume you have Python 2.7 and Paramiko installed. 


#Contents

cisco-01.py :  Login via ssh, enter priviliged mode, and issue a command 
