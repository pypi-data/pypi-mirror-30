#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2017 Alex Epstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
from sys import platform
from os import system

import requests
from colorclass import Color
from terminaltables import AsciiTable

import cryptoUtils.cwconfig as cfg

config = cfg.config()


def request(url, params=None):
    """
    Parameter url: url to request
    Output: JSON ready response from the server
    Logic:
        - Request the url
        - Check for successful status code from server
        - Return the JSON response
    """
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def clear():
    """
    Output: Clears the terminal
    Logic:
        - We just want to know how to clear the terminal
        - Check the platform type
        - Clear the terminal in the right way
    """
    if platform in ("linux", "linux2", "darwin"):
        system("clear")
    elif platform == "win32":
        system("cls")
    else:
        print("Uh-oh you are using an unsupported system :/")


def get_total_crypto(coin_type):
    """
    Output: Total crypto across all addresses in the config class
    Parameters:
        - Cointype: Which coin do you want the total crypto for
    Logic:
        - Start with 0 total crypto
        - For every respective address in the config file
            - Request respective api for balance
            - Add this balance to the total crypto
        - Return the total crypto
    """
    total_crypto = 0.0
    if coin_type == "bitcoin":
        for address in config.bitcoinAddress:
            try:
                url = "https://blockchain.info/rawaddr/" + address
                response = request(url)
                total_crypto += float(response['final_balance']) / pow(10, 8)
            except Exception:
                pass
    elif coin_type == "ethereum":
        for address in config.etherAddress:
            try:
                url = "https://api.blockcypher.com/v1/eth/main/addrs/" + address
                response = request(url)
                total_crypto += float(response['final_balance']) / pow(10, 18)
            except Exception:
                pass
    elif coin_type == "litecoin":
        for address in config.litecoinAddress:
            try:
                url = ("https://chain.so/api/v2/get_address_balance/LTC/"
                       + address)
                response = request(url)
                total_crypto += float(response['data']['confirmed_balance'])
            except Exception:
                pass
    elif coin_type == "bitcoin-cash":
        for address in config.bitcoinCashAddress:
            try:
                url = (
                    "https://cashexplorer.bitcoin.com/api/addr/"
                    + address
                    + "/balance"
                )
                response = request(url)
                total_crypto += float(response) / pow(10, 8)
            except Exception:
                pass
    elif coin_type == "dash":
        for address in config.dashAddress:
            try:
                url = ("https://chain.so/api/v2/get_address_balance/DASH/"
                       + address)
                response = request(url)
                total_crypto += float(response['data']['confirmed_balance'])
            except Exception:
                pass
    elif coin_type == "ripple":
        for address in config.rippleAddress:
            try:
                url = ("https://data.ripple.com/v2/accounts/"
                       + address + "/balances")
                response = request(url)
                total_crypto += float(response['balances'][0]['value'])
            except Exception:
                pass
    elif coin_type == "digibyte":
        for address in config.digibyteAddress:
            try:
                url = ("https://digiexplorer.info/api/addr/"
                       + address + "/balance")
                response = request(url)
                total_crypto += float(response) / pow(10, 8)
            except Exception:
                pass
    elif coin_type == "stellar":
        for address in config.stellarAddress:
            try:
                url = "https://horizon.stellar.org/accounts/" + address
                response = request(url)
                total_crypto += float(response['balances'][0]['balance']) if str(response['balances'][0]['asset_type']) == "native" else 0
            except Exception:
                pass
    elif coin_type == "cardano":
        for address in config.cardanoAddress:
            try:
                url = ("https://cardanoexplorer.com/api/addresses/summary/" + address)
                response = request(url)
                total_crypto += float(response["Right"]["caBalance"]["getCoin"]) / pow(10,6)
            except Exception:
                pass
    return total_crypto


def get_crypto_info(coin_type, colored=False):
    """
    Output: Array of metrics related to the respective coin type
    Parameters
        - Cointype: query coinmarketcap about this specified cointype
        - Colored: Do we want the colored version of the output (only
            when sending to terminal do we want this)
    Logic:
        - Request info from coinmarket cap
        - Ready the response for JSON parsing
        - Parse the response and append each piece of info to the
            metrics array
        - Return the metrics array
    """
    metrics = []
    coin_types = ["bitcoin", "ethereum", "litecoin", "bitcoin-cash",
                  "dash", "ripple", "digibyte", "stellar", "cardano"]
    if coin_type not in coin_types:
        raise ValueError("Invalid coin_type")
    url = "https://api.coinmarketcap.com/v1/ticker/" + coin_type
    params = {'convert': config.fiatCurrency}
    response = request(url, params)
    total_crypto = get_total_crypto(coin_type)
    if not colored:
        metrics.append(response[0]['price_' + config.fiatCurrency.lower()])
        metrics.append(
            response[0]['24h_volume_' + config.fiatCurrency.lower()]
        )
        metrics.append(response[0]['percent_change_7d'])
        metrics.append(response[0]['percent_change_24h'])
        metrics.append(response[0]['percent_change_1h'])
        metrics.append(total_crypto)
        metrics.append(
            total_crypto
            * float(response[0]['price_' + config.fiatCurrency.lower()])
        )
    else:
        metrics.append(Color(
            "{autogreen}"
            + response[0]['price_' + config.fiatCurrency.lower()]
            + "{/autogreen}"
        ))
        metrics.append(Color(
            "{autogreen}"
            + response[0]['24h_volume_' + config.fiatCurrency.lower()]
            + "{/autogreen}"
        ))
        if float(response[0]['percent_change_7d']) >= 0:
            metrics.append(Color(
                "{autogreen}"
                + response[0]['percent_change_7d']
                + "{/autogreen}"
            ))
        else:
            metrics.append(Color(
                "{autored}"
                + response[0]['percent_change_7d']
                + "{/autored}"
            ))
        if float(response[0]['percent_change_24h']) >= 0:
            metrics.append(Color(
                "{autogreen}"
                + response[0]['percent_change_24h']
                + "{/autogreen}"
            ))
        else:
            metrics.append(Color(
                "{autored}"
                + response[0]['percent_change_24h']
                + "{/autored}"
            ))
        if float(response[0]['percent_change_1h']) >= 0:
            metrics.append(Color(
                "{autogreen}"
                + response[0]['percent_change_1h']
                + "{/autogreen}"
            ))
        else:
            metrics.append(Color(
                "{autored}"
                + response[0]['percent_change_1h']
                + "{/autored}"
            ))
        metrics.append(Color(
            "{autocyan}"
            + str(total_crypto)
            + "{/autocyan}"
        ))
        metrics.append(
            float(total_crypto)
            * float(response[0]['price_' + config.fiatCurrency.lower()])
        )

    return metrics

def create_header_footer(coinMetrics, colored=True):
    total_fiat = 0
    for metrics in coinMetrics: total_fiat += metrics[-1]
    if colored:
        header = [
            Color("{automagenta}Coin Type{/automagenta}"),
            Color(
                "{automagenta}Price "
                + config.fiatCurrency
                + "{/automagenta}"
            ),
            Color("{automagenta}24h Volume{/automagenta}"),
            Color("{automagenta}7d % Change{/automagenta}"),
            Color("{automagenta}24h % Change{/automagenta}"),
            Color("{automagenta}1h % Change{/automagenta}"),
            Color("{automagenta}Crypto Balance{/automagenta}"),
            Color(
                "{automagenta}"
                + config.fiatCurrency.upper()
                + " Balance"
                + "{/automagenta}"
            )
        ]
        coinMetrics[0].insert(0, Color("{autocyan}Bitcoin      (BTC){/autocyan}"))
        coinMetrics[1].insert(0, Color("{autocyan}Ethereum     (ETH){/autocyan}"))
        coinMetrics[2].insert(0, Color("{autocyan}Litecoin     (LTC){/autocyan}"))
        coinMetrics[3].insert(
                              0, Color("{autocyan}Bitcoin Cash (BCH){/autocyan}"))
        coinMetrics[4].insert(0, Color("{autocyan}Dash         (DSH){/autocyan}"))
        coinMetrics[5].insert(0, Color("{autocyan}Ripple       (XRP){/autocyan}"))
        coinMetrics[6].insert(0, Color("{autocyan}Digibyte     (DGB){/autocyan}"))
        coinMetrics[7].insert(0, Color("{autocyan}Stellar      (XLM){/autocyan}"))
        coinMetrics[8].insert(0, Color("{autocyan}Cardano      (ADA){/autocyan}"))
        footer = Color(
            "{automagenta}Last Updated: %s{/automagenta}\t\t\t\t\t\t\t      "
            "{autogreen}Total %s: %.2f{/autogreen}"
            % (str(datetime.now()), config.fiatCurrency, total_fiat)
        )
    else:
        header = [
                "Coin Type",
                "Price " + config.fiatCurrency,
                "24h Volume",
                "7d % Change",
                "24h % Change",
                "1h % Change",
                "Crypto Balance",
                config.fiatCurrency.upper() + " Balance"
        ]
        coinMetrics[0].insert(0, "Bitcoin      (BTC)")
        coinMetrics[1].insert(0, "Ethereum     (ETH)")
        coinMetrics[2].insert(0, "Litecoin     (LTC)")
        coinMetrics[3].insert(0, "Bitcoin Cash (BCH)")
        coinMetrics[4].insert(0, "Dash         (DSH)")
        coinMetrics[5].insert(0, "Ripple       (XRP)")
        coinMetrics[6].insert(0, "Digibyte     (DGB)")
        coinMetrics[7].insert(0, "Stellar      (XLM)")
        coinMetrics[8].insert(0, "Cardano      (ADA)")
        footer = ("Last Updated: %s \t\t\t\t\t\t\t      Total %s: %.2f"
                      % (str(datetime.now()), config.fiatCurrency, total_fiat))
    return header, footer


def get_crypto_table(clear_console=False, colored=True):
    """
    Output: Returns an ascii table for all cryptocurrencies and their data
    Parameters:
        - clearConsole: Do we want to clear the console before
            returning this data (we do want to do this when running in
            monitor mode)
        - Colored: Do we want the table to be colored
    Logic:
        - Create header
        - Get metrics on each legal currency and insert into their own
            array
        - Get the total fiat by adding the last index of each metrics
            array together
        - Insert cointypes into the respective array
        - Combine the header and the crypto metrics into one big
            metrics array
        - Create the ascii table from this data and return it
    """
    metrics = []
    bitcoin_metrics = get_crypto_info("bitcoin", colored)
    ethereum_metrics = get_crypto_info("ethereum", colored)
    litecoin_metrics = get_crypto_info("litecoin", colored)
    bitcoin_cash_metrics = get_crypto_info("bitcoin-cash", colored)
    dash_metrics = get_crypto_info("dash", colored)
    ripple_metrics = get_crypto_info("ripple", colored)
    digibyte_metrics = get_crypto_info("digibyte", colored)
    stellar_metrics = get_crypto_info("stellar", colored)
    cardano_metrics = get_crypto_info("cardano", colored)
    coinMetrics = [bitcoin_metrics, ethereum_metrics, litecoin_metrics,
                   bitcoin_cash_metrics, dash_metrics, ripple_metrics,
                   digibyte_metrics, stellar_metrics, cardano_metrics]
    header, footer = create_header_footer(coinMetrics, colored)
    metrics.append(header)
    for metric in coinMetrics: metrics.append(metric)
    table = AsciiTable(metrics)
    if clear_console:
        clear()
    return table.table + "\n" + footer
