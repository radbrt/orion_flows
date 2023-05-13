import logging
import singer

def main():

  LOGGER = logging.getLogger(__name__)
  SINGLOGGER = singer.get_logger()

  SINGLOGGER.info("Starting with the SINGLOGGER")
  SINGLOGGER.debug("This is your SINGLOGGER speaking")
  SINGLOGGER.warning("Please comply with the SINGLOGGER directives")
  SINGLOGGER.error("This has been a public service announcement from the SINGLOGGER")

  LOGGER.info("Starting with the LOGGER")
  LOGGER.debug("This is your LOGGER speaking")
  LOGGER.warning("Please comply with the LOGGER directives")
  LOGGER.error("This has been a public service announcement from the LOGGER")

  logging.info("Now for the built-in logger")
  logging.debug("This is your lowercase logger speaking")
  logging.warning("Please comply with the lowercase logging directives")
  logging.error("This has been a public service announcement from the lowercase logger")


  print("Yay finally a print statement!")

if __name__ == '__main__':
  main()