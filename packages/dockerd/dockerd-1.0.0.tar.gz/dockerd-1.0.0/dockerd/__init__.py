import subprocess
import sys
from contextlib import contextmanager
from functools import partial
from subprocess import CalledProcessError


def _build_args(cmd, *args, **kwargs):
	return cmd + ["--" + name.replace("_", "-") + "=" + str(value) for name, value in kwargs.items()] + list(args)


def _call_docker(subcommand, *args, input=None, **kwargs):
	subprocess.run(_build_args(['docker', subcommand], *args, **kwargs), check=True, input=input)


class DockerCtl:
	__getattr__ = staticmethod(lambda command_name: partial(_call_docker, command_name))
	__call__ = staticmethod(_call_docker)


@contextmanager
def Docker(**kwargs):
	kwargs['storage_driver'] = 'overlay2'
	with subprocess.Popen(_build_args(['dockerd'], **kwargs), stderr=subprocess.PIPE) as dockerd:
		try:
			while True:
				line = dockerd.stderr.readline().decode('utf-8').strip()
				if not line:
					break
				print('dockerd: ' + line, file=sys.stderr)
				sys.stderr.flush()
				if "API listen on" in line:
					break

			yield DockerCtl()
		finally:
			dockerd.kill()
