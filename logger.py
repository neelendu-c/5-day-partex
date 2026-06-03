import logging

logging.basicConfig(level=logging.INFO,filename="log.log",filemode="w",format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Information")
logging.warning("Warning")
logging.error("Error")
logging.critical("Critical error")