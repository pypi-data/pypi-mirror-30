dockerd library spawns your own Docker daemon as a subprocess, lets you run some docker commands, and then kills the daemon when you don't need it anymore.

It works perfectly inside privileged docker containers (achieving docker-in-docker in a faster and more self-contained way than official tutorials)

## Example code
```python
#!/bin/env python3
from dockerd import Docker, CalledProcessError
import sys

with Docker() as docker:
	try:
		docker.pull('lew21/dockerd')
	except CalledProcessError:
		pass

	try:
		docker.build('.', cache_from='lew21/dockerd', pull=True, tag='dockerd')
		docker.tag('dockerd', 'lew21/dockerd')
		docker.push('lew21/dockerd')
	except CalledProcessError as e:
		sys.exit(e.returncode)

```
