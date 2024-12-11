import logging
import warnings

log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

logging.captureWarnings(True)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)
