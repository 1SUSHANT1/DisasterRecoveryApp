import subprocess
from pathlib import Path
import shutil
import getpass

user=getpass.getuser()
if user != "root":
	print("Insufficient Priviledges. Please run as root. Abort")
	exit()

def remService(service):
	subprocess.run(["apt", "remove","-y", service])
	subprocess.run(["apt", "purge", "-y", service])

remService("nginx")
remService("gunicorn")
remService("python3-flask")
remService("git")

subprocess.run(["apt","-y","autoremove"])


home=Path.home()
immutables=Path.home()/"immutables"
if immutables.exists():
	print("Immutables folder exists")
	immutableFire=immutables/"immutableFire.conf"
	
	if immutableFire.exists():
		print("immutableFIre here")
		subprocess.run(["nft","flush","ruleset"])
		loadFire=subprocess.run(["nft","-f",immutableFire])
		fireCode=loadFire.returncode
		if fireCode == 0:
			print("Firewall loaded")
			#shutil.move(immutableFire,immutables/"immutableFireOld")
			subprocess.run(["mv","--backup=numbered",immutableFire,immutables/"immutableFireOld"])
		else:
			print("Firewall couldn't be loaded. Immutable file is left unchanged")
	else:
		print("immutable fire doesnt exist. skipping")

	immutableNGINX=immutables/"immutableNGINX.conf"
	if immutableNGINX.exists():
		print("immutableNGINX here")
		try:
			shutil.copy2(immutableNGINX,"/etc/nginx/nginx.conf")
		except:
			print("immutableNGINX file couldn't be used for recovery. The file is left unchanged")
		else:
			print("immutableNGINX file was used to perform recovery")
			subprocess.run(["mv","--backup=numbered",immutableNGINX,immutables/"immutableNGINXOld"])
			#shutil.move(immutableNGINX,immutables/"immutableNGINXOld")
	else:
		print("immutableNginx doesn't exist. skipping")

else:
	print("Immutables folder doesn't exist")
