# Logging in Prefect

By default, only prefect's own logger is the only one popping up in the prefect flow logs. But there is a separate config that can set in the agent, `PREFECT_LOGGING_EXTRA_LOGGERS`, that allows other loggers to be printed as well.

This flow demonstrates that. It invokes a python script via the command line, and that script logs some lines using non-prefect logging libraries.

The script looks as follows:

```py
import logging
import singer

def main():

  LOGGER = logging.getLogger(__name__)
  SINGLOGGER = singer.get_logger()

  SINGLOGGER.info("A logg message with the SINGLOGGER")
  LOGGER.info("A logg message with the LOGGER")
  logging.info("Now for the built-in logger")

if __name__ == '__main__':
  main()
```

If you run this with an ordinary agent, none of these log lines will show up. But if the agent has the `PREFECT_LOGGING_EXTRA_LOGGERS` config set correctly, the lines show up. This was tested with the following env variable declaration in the k8s manifest:

```yaml
- name: PREFECT_LOGGING_EXTRA_LOGGERS
  value: "logging,singer_sdk,singer-python,singer"
```
