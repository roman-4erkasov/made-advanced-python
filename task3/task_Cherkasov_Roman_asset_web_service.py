import logging
from flask import Flask

LOG_CONFIG_NM = "logging.conf.yml"

logger = logging.getLogger("application_logger")
app = Flask(__name__)


class CDRCrawler:
    BASE = "https://www.cbr.ru/"


@app.route("/")
def hello():
    return "hello!"


@app.errorhandler(404)
def page_not_found(error):
    return "This route is not found", 404

