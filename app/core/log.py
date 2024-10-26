import logging

format = "[%(levelname)s] %(message)s"
logging.basicConfig(format=format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
