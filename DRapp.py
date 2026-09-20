import subprocess
import getpass

def getService(service):
	result=subprocess.run(["apt", "install","-y", service])
	return result.returncode



###################main########################
user=getpass.getuser()
if user != "root":
	print("Insufficient Priviledges. Please run as root. Abort")
	exit()


ng=getService("nginx")
gn=getService("gunicorn")
fl=getService("python3-flask")

