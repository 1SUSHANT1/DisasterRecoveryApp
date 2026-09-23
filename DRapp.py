import subprocess
import getpass
from pathlib import Path
import shutil

def getService(service):
	result=subprocess.run(["apt", "install", "-y", service])
	return result.returncode

def installThis(service):
	while True:
		code=getService(service)
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
			desicion=input("Enter 1 to work with the existing directory. Enter 2 to remove the existing directory. Press any other key to restart git clone: ")
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



###################main########################
user=getpass.getuser()
if user != "root":
	print("Insufficient Priviledges. Please run as root. Abort")
	exit()


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


installThis("nginx")
installThis("gunicorn")
installThis("python3-flask")
installThis("git")

defaultRepo="https://github.com/1SUSHANT1/myProjects.git"
rootDir=gitClone(defaultRepo)

rootDir=Path(rootDir)
expPyApp=rootDir
expNgConf=rootDir/"serverConfiguration"/"nginx"
expFiConf=rootDir/"serverConfiguration"/"firewall"

actPyLoc=locateFiles(rootDir,"myPyScript.py","Python",expPyApp)
actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
actFiConf=locateFiles(rootDir,"nftables.conf","Firewall", expFiConf)


print("Python file is at: ", actPyLoc)
print("NGINX file is at: ", actNgConf)
print("Firewall file is at: ", actFiConf)





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

while True:
	fc=subprocess.run(["nft", "-c","-f",actFiConf])
	if fc.returncode != 0:
		print("The Firewall file syntax is invalid")
		choice=input("Enter 1 to provide another file. Press any other key to exit: ")
		if choice == "1":
			actFiConf=locateFiles(rootDir,"nftables.conf","Firewall", expFiConf)
			continue
		else:
			exit()
	else:
		print("The Firewall file syntax is valid")
		break

originalFile=""
recoverFlag=False

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
			shutil.copy(actNgConf,"/etc/nginx/conf.d")
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
			filePath=Path("/etc/nginx/conf.d")/fileName
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
			desicion=input("Enter 1 to provide another file. Press any other key to recover the original file and exit")
			if desicion == "1":
				actNgConf=locateFiles(rootDir,"nginx.conf","NGINX", expNgConf)
				continue
			else:
				try:
					shutil.copy(originalFile,"/etc/nginx/nginx.conf")
				except:
					print("The original file couldn't be recovered")
				else:
					print("Original file was successfully recovered")	
					exit()

	else:
		print("The NGINX file syntax is valid")
		break

actPyLocStr= str(actPyLoc)
pyFiName=actPyLocStr.split("/")[-1]


#while True:
#	if (expPyApp/"myPyScript.py").exists():
#		try:
#			shutil.copy(expPyApp/"myPyScript.py",expPyApp/"myPyScriptBack.py")
#		except:
#			print("Original python file exists")


immutables=home/"immutables"
while True:
	writeToImmutableFile=False
	if (immutables/"immutableFire.conf").exists():
		print("Immutable firewall file exists")
	else:
		print("Immutable firewall file doesn't exist. Creating now")
		immutableFirewall=immutables/"immutableFire.conf"	
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

	if backFire.exists():
		print("A backup file already exists. Creating a new one isn't recommended")
		desicion=input("Enter 1 to override the existing backup file (not recommended). Press any other key to skip and continue: ")
		if desicion == "1":
			cuRule=subprocess.run(["nft","list","ruleset"],
			capture_output=True,
			text=True
			).stdout
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
				continue
			elif choice == "2": 
				print("Continuing without writing to the immutable file")
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





