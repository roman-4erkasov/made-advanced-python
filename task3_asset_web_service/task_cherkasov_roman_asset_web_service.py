"""
Asset calculator
"""

import logging
import requests
from flask import Flask, request, jsonify
from lxml import etree
from markupsafe import escape


LOG_CONFIG_NM = "logging.conf.yml"
BASE_URL = "https://www.cbr.ru/"
PG_DAILY = BASE_URL + "eng/currency_base/daily/"
PG_INDICATORS = BASE_URL + "eng/key-indicators/"


IDX_UNIT = 2
IDX_CC = 1
IDX_RATE = 4

logger = logging.getLogger("application_logger")
app = Flask(__name__)
app.bank = list()
app.added_names = set()


@app.errorhandler(404)
def api_page_not_found(_):
    """
    Handler of error 404
    """
    return "This route is not found", 404


def parse_cbr_currency_base_daily(text):
    """
    :param text: html text
    :return: dict of currency rates
    """
    root = etree.fromstring(text, etree.HTMLParser())
    docs_raw = root.xpath("//table[@class='data']//tr")
    results = dict()
    for elm in docs_raw:
        arr = elm.xpath(".//td/text()")
        if len(arr) > 0:
            n_units = int(arr[IDX_UNIT].replace(',', ''))
            code = arr[IDX_CC]
            rate = float(arr[IDX_RATE].replace(',', ''))
            result = rate / n_units

            results[code] = result

    return results


def extract_daily():
    """
    :return: dict of currency rates
    """
    try:
        resp = requests.get(PG_DAILY)
        if not resp.ok:
            return None
        docs = parse_cbr_currency_base_daily(resp.text)
        return docs
    except Exception:
        return None


@app.route("/cbr/daily")
def api_daily():
    """

    :return:
    """
    query = request.url_rule.rule
    app.logger.debug(f"got query: {query}")
    docs = extract_daily()
    if docs is None:
        result = "CBR service is unavailable", 503
    else:
        result = jsonify(docs), 200
    return result


def parse_cbr_key_indicators(text):
    """

    :param text:
    :return:
    """
    xpath_docs = "(//div[@class='table key-indicator_table']//table)[position()<=2]" + \
                 "//tr[not(contains(@class,'denotements'))]"
    root = etree.fromstring(text, etree.HTMLParser())
    docs_raw = root.xpath(xpath_docs)
    results = dict()
    for doc_raw in docs_raw:
        key = doc_raw.xpath(
            ".//div[@class='col-md-3 offset-md-1 _subinfo']/text()")[0]
        value = float(doc_raw.xpath(".//td/text()")[-1].replace(',', ''))
        results[key] = value
    return results


def extract_key_indicators():
    """

    :return:
    """
    try:
        resp = requests.get(PG_INDICATORS)
        if not resp.ok:
            return None
        docs = parse_cbr_key_indicators(resp.text)
        return docs
    except Exception:
        return None


@app.route("/cbr/key_indicators")
def api_key_indicators():
    """

    :return:
    """
    query = request.url_rule.rule
    app.logger.debug(f"got query: {query}")
    docs = extract_key_indicators()
    if docs is None:
        result = "CBR service is unavailable", 503
    else:
        result = jsonify(docs), 200
    return result


@app.route("/api/asset/add/<string:char_code>/<string:name>/<float:capital>/<float:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<float:capital>/<int:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<int:capital>/<float:interest>")
@app.route("/api/asset/add/<string:char_code>/<string:name>/<int:capital>/<int:interest>")
def api_asset_add(char_code: str, name: str, capital, interest):
    """

    :param char_code:
    :param name:
    :param capital:
    :param interest:
    :return:
    """
    char_code_safe = escape(char_code)
    name_safe = escape(name)
    if name_safe not in app.added_names:
        app.bank.append([char_code_safe, name_safe, capital, interest])
        app.added_names.add(name_safe)
        result = f"Asset '{name_safe}' was successfully added", 200
    else:
        result = f"Asset '{name_safe}' is already exist", 403
    return result


@app.route("/api/asset/list")
def api_asset_list():
    """

    :return:
    """
    return jsonify(sorted(app.bank)), 200


@app.route("/api/asset/cleanup")
def api_asset_cleanup():
    """

    :return:
    """
    app.bank = list()
    app.added_names = set()
    return "The list of assets was successfully cleaned up", 200


@app.route("/api/asset/get")
def api_asset_get():
    """

    :return:
    """
    names = {escape(name) for name in request.args.getlist('name')}
    result = sorted(filter(lambda x: x[1] in names, app.bank))
    return jsonify(result), 200


@app.route("/api/asset/calculate_revenue")
def api_asset_calculate_revenue():
    """

    :return:
    """
    map1 = extract_key_indicators()
    map2 = extract_daily()

    periods = sorted([int(p) for p in request.args.getlist("period")])

    results = dict()
    for period in periods:
        result = 0
        for char_code, _, capital, interest in app.bank:
            capital_rub = None
            if char_code in map1:
                capital_rub = capital * map1[char_code]
            elif char_code in map2:
                capital_rub = capital * map2[char_code]
            if capital_rub is not None:
                result += capital_rub * ((1.0 + interest) ** period - 1.0)
        results[f"{period}"] = f"{result}"

    return jsonify(results), 200
