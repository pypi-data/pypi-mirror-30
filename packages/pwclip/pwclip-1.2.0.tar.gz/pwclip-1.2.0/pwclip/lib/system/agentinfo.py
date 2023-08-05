from os import environ, stat as osstat

from stat import S_ISSOCK as issock

from system.user import userfind

def gpgagentinfo(user=None):
	uid = int(userfind(userfind(), 'uid'))
	rundir = '/run/user/%d/gnupg'%uid
	gpgsock, sshsock = '%s/S.gpg-agent'%rundir, '%s/S.gpg-agent.ssh'%rundir
	environ['GPG_AGENT_INFO'] = '%s:0:1'%gpgsock
	environ['SSH_AUTH_SOCK'] = sshsock
	return gpgsock, sshsock
