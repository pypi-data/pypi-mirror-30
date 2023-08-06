# raven-bash
[![PyPi package version](https://badge.fury.io/py/raven-bash.png?v)](https://badge.fury.io/py/raven-bash)
    
Raven Sentry client for Bash.

Logs error if one of your commands exits with non-zero return code and produces simple traceback for easier debugging. It also tries to extract last values of the variables visible in the traceback. Environment variables and stderr output are also included.

Bash does not provide much of the debugging capabilities known from the higher level languages so the capabilities are somewhat limited. However it works just fine for simple bash scripts used for deployment, monitoring, starting/stopping services, etc.

This script is currently in working beta. Use at your own risk. Any contributions are highly appreciated.

![Sentry screenshot](https://upx.cz/yll8sbt7jsm991cssgoieb0akdpkl799lk3cea55)

## Installation
```shell
pip install raven-bash
```

## Usage
1. Create the file `/etc/raven-bash.conf` with the following content:
  ```ini
  [DEFAULT]
  
  # replace with your DSN
  SENTRY_DSN = https://key:secret@your_sentry_domain/project_id
  ```
  Additionally you can use `SENTRY_DSN` environment variable which will override any settings defined in configuration file.

2. Add `source raven-bash` to the beginning of your bash scripts, e.g.:
  ```bash
  #!/bin/bash
  source raven-bash  # sentry reporting
  
  echo "Hello world!"
  echo "This will produce an error" | grep "success"
  ```
  Scripts you include using `source` or `.` will be monitored automatically. Any other scripts you execute won't be monitored unless you add `source raven-bash` to them.
  
## Caveats
This script works only with `set -e` (enabled automatically) bash option which means that any command returning non-zero return code will produce an error and stop the execution. If some of your commands is returning non-zero return code and it is not an error you can prevent this from happening for example by piping it's output to `| true`.

When running your scripts as cron jobs please be aware of possibly different `PATH` settings. `source raven-bash` will not work with incorrect `PATH`. This can be fixed by specifying environment variable in crontab, eg.:

```bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# m h  dom mon dow   command
# your commands
```

## Known bugs
Will be hopefully fixed in one of the future releases.

* **stderr output is discarded when your program exits correctly**
* "traceback" works only for the last included file
* Unrelated package versions are added to the request (this is due to `raven-python` which collects additional data from Python interpreter)
