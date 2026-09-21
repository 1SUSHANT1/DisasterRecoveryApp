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
		if (expPyApp/file).exists():
			print(name, "file found")
			return (expPyApp/file)
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







