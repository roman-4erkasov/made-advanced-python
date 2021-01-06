import logging

import requests
from flask import Flask, request, abort, jsonify
from lxml import etree

LOG_CONFIG_NM = "logging.conf.yml"
BASE_URL = "https://www.cbr.ru/"
PG_DAILY = BASE_URL+"eng/currency_base/daily/"
PG_INDICATORS = BASE_URL+"eng/key-indicators/"

PARSING_MAP = {
    "/cbr/daily": PG_DAILY,
    "/cbr/key_indicators": PG_INDICATORS
}

IDX_UNIT = 2
IDX_CC = 1
IDX_RATE = 4


logger = logging.getLogger("application_logger")
app = Flask(__name__)
app.bank = list()

# class CDRCrawler:

# def parse_daily():
#     # request.
#     breakpoint()


@app.errorhandler(404)
def api_page_not_found(_):
    return "This route is not found", 404


def parse_daily(text):
    root = etree.fromstring(text, etree.HTMLParser())
    docs_raw = root.xpath("//table[@class='data']//tr")
    results = dict()
    for elm in docs_raw:
        arr = elm.xpath(".//td/text()")
        if len(arr)>0:
            # breakpoint()
            n_units = int(arr[IDX_UNIT])
            code = arr[IDX_CC]
            rate = float(arr[IDX_RATE])
            result = rate/n_units

            results[code] = result

    return results


@app.route("/cbr/daily")
def api_daily():
    query = request.url_rule.rule
    resp = requests.get(PARSING_MAP[query])
    app.logger.debug(f"got query: {query}")
    if not resp.ok:
        abort(503)
    docs = parse_daily(resp.text)
    # return jsonify(
    #     {
    #         "documents": docs,
    #         "version": 1.0
    #     }
    # )
    return jsonify(docs)


def parse_key(text):
    xpath_docs = "(//div[@class='table key-indicator_table']//table)[position()<=2]" + \
        "//tr[not(contains(@class,'denotements'))]"
    root = etree.fromstring(text, etree.HTMLParser())
    docs_raw = root.xpath(xpath_docs)
    results = dict()
    for doc_raw in docs_raw:
        # breakpoint()
        key = doc_raw.xpath(".//div[@class='col-md-3 offset-md-1 _subinfo']/text()")[0]
        value = doc_raw.xpath(".//td/text()")[-1]
        results[key] = value
    return results
# def parse_key_met(text):
#     xpath_docs = "(//div[@class='table key-indicator_table']//table)[2]//tr[not(contains(@class,'denotements'))]"
#     root = etree.fromstring(text, etree.HTMLParser())
#     docs_raw = root.xpath(xpath_docs)
#     results = dict()
#     for doc_raw in docs_raw:
#         key = doc_raw.xpath(".//div[@class='col-md-3 offset-md-1 _subinfo']/text()")
#         value = doc_raw.xpath(


@app.route("/cbr/key_indicators")
def api_key_indicators():
    try:
        query = request.url_rule.rule
        resp = requests.get(PARSING_MAP[query])
        app.logger.debug(f"got query: {query}")
        if not resp.ok:
            return "CBR service is unavailable", 503
        docs = parse_key(resp.text)
        return jsonify(docs)
    except:
        return "CBR service is unavailable", 503


class Asset

@app.route("/api/asset/add/<string:char_code>/<string:name>/<float:capital>/<float:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<float:capital>/<int:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<int:capital>/<float:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<int:capital>/<int:interest>")
def api_add_asset(char_code:str,name:str, capital,interest):
    pass

