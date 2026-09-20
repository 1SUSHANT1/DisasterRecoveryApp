import subprocess
import getpass

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

def gitClone():
	defaultRepo="https://github.com/1SUSHANT1/myProjects.git"
	dirName=defaultRepo.split("/")[-1].removesuffix(".git")
	print(dirName)

	subprocess.run(["git","clone",defaultRepo])

###################main########################
user=getpass.getuser()
if user != "root":
	print("Insufficient Priviledges. Please run as root. Abort")
	exit()


installThis("nginx")
installThis("gunicorn")
installThis("python3-flask")
installThis("git")
gitClone()
