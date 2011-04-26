from logging import DEBUG

PORT = 6808
PID_FILENAME = '/var/run/virid.pid'
CERTIFICATE_FILENAME = 'keys/virid.cert'
TASK_DIR = 'tasks'
DATA_DIR = 'data'
LOG_FILENAME = None
LOG_LEVEL = DEBUG
LOG_FORMAT = '%(levelname)s::%(asctime)s::%(message)s'
LOG_REQUESTS = True
APP_NAME = 'viri'
APP_VERSION = '0.0.1'
APP_DESC = 'Distributes and remotely executes Python tasks'

