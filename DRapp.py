import subprocess
import getpass
from pathlib import Path
import shutil
import psutil
import psycpog
########################INSTALLS SERVICES#######################################
def installThis(service,OS):
	while True:
		if OS=="debian":
			code=(subprocess.run(["apt", "install", "-y", service])).returncode
		elif OS=="alpine":
			code=(subprocess.run(["apk","add",service])).returncode
		else:
			print("Operating system not supported. Fatal. Abort")
			exit()
		if code == 0:
			print(service, "successfully installed.")
			break
		else:
			print(service, "installation failed")
			choice=input("Enter 1 to try again. Enter any other key to quit")
			if choice == "1":
				continue
			else:
				print(serice,"couldn't be installed. Fatal Abort")
				exit()

############################################CLONES REMOTE REPO##########################
def gitClone(defaultRepo):
	while True:
		print("This is the default repo:", defaultRepo)
		choice=input("Enter 1 to use the default repo. Enter 2 to use a custom repo. Enter any other key to exit: ")
		usingRepo=""
		if choice == "1":
			usingRepo=defaultRepo
		elif choice == "2":
			usingRepo=input("Enter your custom GitHub repo")
		else:
			print("FATAL. Git clone unsuccessful. Abort")
			exit()

		dirName=usingRepo.split("/")[-1].removesuffix(".git")
		print(dirName)

		alreadyEx=Path(dirName)
		if alreadyEx.exists():
			print("Directory already exists")
			desicion=input("Enter 1 to work with the existing directory. Enter 2 to remove the existing directory and get a fresh copy. Press any other key to restart git clone: ")
			if desicion == "1":
				print("Using the existing directory")
				return(dirName)
				break
			elif desicion == "2":
				conf=input(f"WARNING: This will remove the existing {dirName} directory. Enter C to proceed. Press any other key to restart git clone: ")
				if conf == "C":
					print("Removing the existing directory")
					try:
						shutil.rmtree(alreadyEx)
					except Exception as e:
						print("Existing directory couldn't be removed.",e," Please try again")
						continue
					clcode=subprocess.run(["git","clone",usingRepo]).returncode
					if clcode == 0:
						print("Remote Repo successfully cloned.")
						return(dirName)
						break
					else:
						print("Remote Repo couldn't be cloned. Please try again")
						continue
				else:
					continue
		else:
				clcode=subprocess.run(["git","clone",usingRepo]).returncode
				if clcode == 0:
					print("Remote Repo successfully cloned.")
					return(dirName)
					break
				else:
					print("Remote Repo couldn't be cloned. Please try again")
					continue

####################################LOCATES FILES####################################
def locateFiles(rootDir,file,name,expDir):
	while True:
		expLoc=expDir/file
		if (expLoc).exists():
			print(name, "file found at:",expLoc)
			choice=input(f"Enter 1 if you want to provide a different {name} file. Press any other key to use the default {file} file: ")
			if choice == "1":
				loc=input(f"Enter the path to the {name} file. The path should start from {rootDir}: ") 
				loc=Path(loc)
				if loc.exists():
					with open (loc,"r") as file:
						print(file.read())
					print(name, "file located")
					return loc
				else:
					print("The file couldn't be located")
					cont=input("Enter 1 to try again. Press any other key to exit: ")
					if cont == "1":
						continue
					else:
						exit()
			else:
				return (expLoc)
		else:
			print(name," file wasn't found")
			existence=input(f"Enter 1 if the repository contains the {name} file. Press any other key to exit: ")
			if existence == "1":
				loc=input(f"Enter the path to the {name} file. The path should start from {rootDir}: ") 
				loc=Path(loc)
				if loc.exists():
					print(name, "file located")
					return loc
				else:
					print("The file couldn't be located")
					cont=input("Enter 1 to try again. Press any other key to exit: ")
					if cont == "1":
						continue
					else:
						exit()
			else:
				exit()

##################################INSTALLS CERTBOT DEPENDENCIES######################
def certPrep():
	result=0
	a=subprocess.run(["apt", "install", "python3", "python3-dev", "python3-venv", "libaugeas-dev", "gcc"])
	result=result+a.returncode
	b=subprocess.run(["python3", "-m", "venv", "/opt/certbot/"])
	result=result+b.returncode
	c=subprocess.run(["/opt/certbot/bin/pip", "install", "certbot", "certbot-nginx"])
	result=result+c.returncode

	return result

###############################RUNS CERTBOT#############################
def installCert():
	a=subprocess.run(["/opt/certbot/bin/certbot","--nginx"])
	if a.returncode!=0:
		print("Certificate installation has failed")
		choice=input("Enter 1 to try again. Press any other key to skip: ")
		if choice == "1":
			installCert()

#################################CREATES A GROUP####################
def addGroup(group):
	gA=subprocess.run(["groupadd",group])
	if gA.returncode==9:
		return 0
	else:
		return gA.returncode


#################################ADDS USER TO GROUP#####################
def addToGroup(user,group):
	aN=subprocess.run(["groupmod","-aU",user,group])
	return aN.returncode


###################################ENABLES SERVICES ON STARTUP###################
def startSv(service,OS):
	if OS=="debian":
		sR=subprocess.run(["systemctl", "start",service])
		sT=subprocess.run(["systemctl", "enable", service])
	elif OS=="alpine":
		sR=subprocess.run(["rc-service",service,"start"])
		sT=subprocess.run(["rc-update","add",service,"default"])
	if sR.returncode==0:
		print(f"{service} was successfully started")
	else:
		print(f"{service} couldn't be started")
	if sT.returncode==0:
		print(f"{service} was successfully enabled")
	else:
		print(f"{service} couldn't be enabled")

#################################DEB GUNICORN HANDLING##################
def gunicornDeb(actGuLoc,rootDir,expGuConf):
	while True:
		checkFile=Path("/tmp/gunicorn.service")
		shutil.copy(actGuLoc,checkFile)
		verifyGunicorn=subprocess.run(["systemd-analyze","verify",checkFile])
		checkFile.unlink()

		if verifyGunicorn.returncode==0:
			try:
				shutil.copy(actGuLoc,"/etc/systemd/system/gunicorn.service")
			except:
				print("Gunicorn systemd service couldn't be created")
				break
			else:
				print("Gunicorn systemd service created")
				break
		else:
			print("Gunicorn configuration file failed syntax check")
			choice=input("Enter 1 to provide another file. Press any other key to skip")
			if choice=="1":
				actGuLoc=locateFiles(rootDir,"gunicornDebian","Gunicorn",expGuConf)
				continue
			else:
				break
###########################ALP GUNICORN HANDLING#############################
def gunicornAlp(actGuLoc,rootDir,expGuConf):
	while True:
		checkFile=Path("/tmp/gunicorn")
		shutil.copy(actGuLoc,checkFile)
		verifyGunicorn=subprocess.run(["sh","-n",checkFile])
		checkFile.unlink()

		if verifyGunicorn.returncode==0:
			try:
				shutil.copy(actGuLoc,"/etc/init.d/gunicorn")
			except:
				print("Gunicorn systemd service couldn't be created")
				break
			else:
				print("Gunicorn systemd service created")
				break
		else:
			print("Gunicorn configuration file failed shell syntax check")
			choice==input("Enter 1 to ignore and proceed. Press any other key to provide another file")
			if input=="1":
				try:
					shutil.copy(actGuLoc,"/etc/init.d/gunicorn")
				except:
					print("Gunicorn systemd service couldn't be created")
					break
				else:
					print("Gunicorn systemd service created")
					break
			else:
				actGuLoc=locateFiles(rootDir,"gunicornAlpine","Gunicorn",expGuConf)
				continue

################################MAIN########################

#############################VERIFY USER#####################
user=getpass.getuser()
if user != "root":
	print("Insufficient Priviledges. Please run as root. Abort")
	exit()

#########################OS DETECTION#######################
OS=""
with open ("/etc/os-release") as file:
	for line in file:
		idField=line.strip().split("=")
		if idField[0]=="ID":
			OS=idField[1]
			break
print(f"Operating system: {OS}")

firewallFile=""
if OS=="debian":
	firewallFile="nftables.conf"
	nginxSFLoc="/etc/nginx/conf.d"
	gunicornFileName="gunicornDebian"
elif OS=="alpine":
	firewallFile="nftables.nft"
	nginxSFLoc="/etc/nginx/http.d"
	gunicornFileName="gunicornAlpine"

############################IMMUTABLE DIRECTORY CREATION##################
home=Path.home()
if (home/"immutables").exists():
	print("Immutables directory already exists")
else:
	try:
		(home/"immutables").mkdir()
	except:
		print("immutables directory could not be created. The app will exit")
		exit()
	else: 
		print("Immutables directory was created")
immutables=home/"immutables"

##############################INSTALL SERVICES###################
installThis("nginx",OS)
installThis("gunicorn",OS)
installThis("python3-flask",OS)
installThis("git",OS)

defaultRepo="https://github.com/1SUSHANT1/myProjects.git"
rootDir=gitClone(defaultRepo)
rootDir=Path(rootDir)

#################################EXPECTED FILE LOCATIONS#############
expPyApp=rootDir
expNgConf=rootDir/"serverConfiguration"/"nginx"
expFiConf=rootDir/"serverConfiguration"/"firewall"
expGuConf=rootDir/"serverConfiguration"/"gunicorn"

#####################################ACTUAL FILE LOCATIONS###########
actGuLoc=locateFiles(rootDir,gunicornFileName,"Gunicorn",expGuConf)
actPyLoc=locateFiles(rootDir,"myPyScript.py","Python",expPyApp)
actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
actFiConf=locateFiles(rootDir,firewallFile,"Firewall", expFiConf)

#print("Python file is at: ", actPyLoc)
#print("NGINX file is at: ", actNgConf)
#print("Firewall file is at: ", actFiConf)

#########################PYTHON FILE SYNTAX#######################
while True:
	pc=subprocess.run(["python3", "-m", "py_compile",actPyLoc])
	if pc.returncode != 0:
		print("The python app syntax is invalid")
		choice=input("Enter 1 to provide another file. Press any other key to exit: ")
		if choice == "1":
			actPyLoc=locateFiles(rootDir,"myPyScript.py","Python",expPyApp)
			continue
		else:
			exit()
	else:
		print("The python app syntax is valid")
		break

#########################FIREWALL CONFIGURATION FILE SYNTAX###############
while True:
	fc=subprocess.run(["nft", "-c","-f",actFiConf])
	if fc.returncode != 0:
		print("The Firewall file syntax is invalid")
		choice=input("Enter 1 to provide another file. Press any other key to exit: ")
		if choice == "1":
			actFiConf=locateFiles(rootDir,firewallFile,"Firewall", expFiConf)
			continue
		else:
			exit()
	else:
		print("The Firewall file syntax is valid")
		break

originalFile=""
recoverFlag=False

##########################NGINX CONFIGURATION FILE SYNTAX AND LOCATE###############
while True:
	whichFile=input("Enter 1 if the NGINX file is the main configuration file. Enter 2 if it is the server configuration file: ")
	if whichFile !="1" and whichFile != "2":
		desicion=input("Invalid input. Enter 1 to try again. Press any other key to exit: ")
		if desicion == "1":
			continue
		else:
			exit()

	try:
		if whichFile == "1":
			try:
				shutil.copy("/etc/nginx/nginx.conf","/etc/nginx/nginxBack.conf")
			except:
				print("Backup couldn't be made")
				choice=input("Enter 1 to provide another file. Enter 2 to ignore and proceed. Press any other key to exit: ")
				if choice == "1":
					actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
					continue
				elif choice == "2":
					conf=input("This will remove the original configuration file without backup. Enter C to continue. Press any other key to try again")
					if conf == "C":
						print("Proceeding without the creating the backup")
					else:
						continue
				else:
					exit()
			else:
				originalFile=Path("/etc/nginx/nginxBack.conf")
				print("Original file was copied to:",originalFile)
				recoverFlag=True

			shutil.copy(actNgConf,"/etc/nginx/")
		else:
			shutil.copy(actNgConf,nginxSFLoc)
	except:
		print("The file could not be copied. Please try again. You might want to run the cleanUp.py app if the problem persists")
		choice=input("Enter 1 to provide another file. Press any other key to exit: ")
		if choice == "1":
			actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
			continue
		else:
			exit()
	else:
		print("NGINX file copied to the nginx directory")
		confStr=str(actNgConf)
		fileName=confStr.split("/")[-1]
		print("Filename is: ",fileName)

		if recoverFlag==False:
			filePath=Path(nginxSFLoc)/fileName
			print("FilePath is: ", filePath)
		else:
			filePath=Path("/etc/nginx")/fileName
			print("FilePath is: ", filePath)

	nc=subprocess.run(["nginx","-t","-c","/etc/nginx/nginx.conf"])
	if nc.returncode != 0:

		if recoverFlag == False:

			print("The NGINX configuration file is invalid. This file should be removed")
			try:
				filePath.unlink()
			except:
				print("file couldn't be removed")
				choice=input("Enter 1 to provide another file. Press any other key to exit: ")
				if choice == "1":
					actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
					continue
				else:
					exit()
			else:
				print("The file was removed")
				desicion=input("Enter 1 if you want to provide another file. Press any other key to exit: ")
				if desicion == "1":
					actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
					continue
				else:
					exit()

		else:
			print("The NGINX configuration file is invalid")
			try:
				shutil.copy(originalFile,nginxSFLoc)
			except:
				print("The original file couldn't be recovered. This may cause problems.")
			else:
				print("Original file was successfully recovered")	

			desicion=input("Enter 1 to provide another file. Press any other key to exit: ")
			if desicion == "1":
				actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
				continue
			else:
				exit()

	else:
		print("The NGINX file syntax is valid")


	if (immutables/"immutableNGINX.conf").exists(): 
			print("Immutable NGINX file exists")
	elif recoverFlag == True:
		print("Immutable NGINX  file doesn't exist. Creating now")
		immutableNGINX=immutables/"immutableNGINX.conf"
		try:
			shutil.copy(nginxSFLoc,immutableNGINX)
		except:
			print("Couldn't create the Immutable NGINX file")
			choice=input("Enter 1 to try again. Enter 2 to continue without creating the immutable file. Press any other key to exit")
			if choice == "1":
				continue
			elif choice == "2": 
				print("Continuing without creating the immutable file")
#				break
			else:
				exit()
		else:
			print("Immutable NGINX file was created")
	break


#########################LOADING FIREWALL######################
while True:
	writeToImmutableFile=False
	if (immutables/firewallFile).exists():
		print("Immutable firewall file exists")
	else:
		print("Immutable firewall file doesn't exist. Creating now")
		immutableFirewall=immutables/firewallFile
		try:
			immutableFirewall.touch()
		except:
			print("Couldn't create the Immutable firewall file")
			choice=input("Enter 1 to try again. Enter 2 to continue without creating the immutable file. Press any other key to exit")
			if choice == "1":
				continue
			elif choice == "2": 
				print("Continuing without creating the immutable file")
			else:
				exit()
		else:
			print("Immutable firewall file was created")
			writeToImmutableFile=True

	backFire=expFiConf/"backFire.conf"

	cuRule=subprocess.run(["nft","list","ruleset"],
	capture_output=True,
	text=True
	).stdout

	if backFire.exists():
		print("A backup file already exists. Creating a new one isn't recommended")
		desicion=input("Enter 1 to override the existing backup file (not recommended). Press any other key to skip and continue: ")
		if desicion == "1":
			backFire.write_text(cuRule)
			print("new backup file was created")
		else:
			print("Proceeding with the existing backup file")


	if writeToImmutableFile == True:
		try:
			immutableFirewall.write_text(cuRule)
		except:
			print("Couldn't write to the Immutable firewall file")
			choice=input("Enter 1 to try again. Enter 2 to continue without writing to the immutable file. Press any other key to exit")
			if choice == "1":
				immutableFirewall.unlink()
				continue
			elif choice == "2": 
				print("Continuing without writing to the immutable file")
				immutableFirewall.unlink()
			else:
				exit()
		else:
			print("Immutable firewall backup created")


	loadFirewall=subprocess.run(["nft","-f",actFiConf])
	fireCode=loadFirewall.returncode
	if fireCode == 0:
		print("The firewall configuration file was correctly loaded into nft")
		break
	else:
		print("The firewall configuration file wasn't loaded into nft")
		choice=input("Enter 1 to try again. Press any other use the existing firewall rules")
		if choice =="1":
			continue
		else:
			print("Using the existing firewall rules")
			break

###############GUNICORN FILE SYNTAX AND LOCATION##################

if OS=="debian":
	gunicornDeb(actGuLoc,rootDir,expGuConf)
elif OS=="alpine":
	gunicornAlp(actGuLoc,rootDir,expGuConf)


##########################GUNICORN USER CREATION#############################
gUser=input("Enter 1 to enter a custom gunicorn user. Press any other key to use the default \"gunicorn\" user: ")
if gUser=="1":
	gunicorn=input("Enter the name of the gunicorn user: ")
else:
	gunicorn="gunicorn"

addGUser=subprocess.run(["useradd","-mr",gunicorn])
if addGUser.returncode==0 or addGUser.returncode==9:
	print("Gunicorn user created")
else:
	print("Failed to user Gunicorn user")


#################################START SERVICES######################
startSv("gunicorn",OS)
startSv("nginx",OS)

##########################PREPARATION FOR USERS AND PERMISSONS###############
nginx=""

for process in psutil.process_iter(["name", "username", "cmdline"]):
	info = process.info
	cmdline = " ".join(info["cmdline"] or [])

	if info["name"] == "nginx" and "worker process" in cmdline:
		nginx = info["username"]
		break
else:
	if OS=="debian":
		nginx="www-data"
	elif OS=="alpine":
		nginx="nginx"

group="webManagers"
#nginx="www-data"

curDir=Path.cwd()
curDir=str(curDir)
traverseThis=curDir.split("/")
traverseThis.pop(0)

#####################CREATE GROUP, USERS AND MANAGE PERMISSIONS##################
if addGroup(group)==0:
	print("Group Added")
	if addToGroup(nginx,group)==0:
		print(f"{nginx} added to {group}")
	else:
		print(f"{nginx} couldn't be added to {group}")

	if addToGroup(gunicorn,group)==0:
		print(f"{gunicorn} added to {group}")
	else:
		printf("{gunicorn} couldn't be added to {group}")


	constructPath=""
	firstDir=True
	for dir in traverseThis:
		constructPath=constructPath+"/"+dir
		print(f"Dir is: {constructPath}")
		if firstDir==True:
			firstDir=False
		else:
			subprocess.run(["chgrp","webManagers",constructPath])
			subprocess.run(["chmod","g+x",constructPath])
	subprocess.run(["chgrp","-R","webManagers",rootDir])
	subprocess.run(["chmod","-R","g+rx",rootDir])

else:
	print("Group wasn't added")


################################PORT FORWARDING################
ipad=subprocess.run(["hostname","-I"],
capture_output=True,
text=True
).stdout;
ipad=ipad.split()[0]
print(f"Please enable port forwarding on your router for the IP address {ipad} at:")
print("TCP port 80")
print("TCP port 443")
print("This will allow HTTP and HTTPS traffic from the internet to reach the computer")

portfor=input(f"Enter 1 if you successfully set the port forwarding. Press any other key to exit: ")

if(portfor!="1"):
	exit()

#################################RUN CERTBOT####################
while True:
	result=certPrep()
	if result != 0:
		print(f"Some certbot dependent actions have failed")
		choice=input("Enter 1 to try again. Press any other key to skip certificate installation: ")
		if choice =="1":
			continue
		else:
			break
	else:
		installCert()
		break

###############################ENABLE AT STARTUP################
