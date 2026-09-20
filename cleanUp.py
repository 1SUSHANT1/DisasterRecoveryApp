import subprocess

def remService(service):
	subprocess.run(["apt", "remove","-y", service])
	subprocess.run(["apt", "purge", "-y", service])
	subprocess.run(["apt", "-y","autoremove"])


remService("nginx")
remService("gunicorn")
remService("python3-flask")
