#! /usr/bin/env python
# -*- coding: utf8 -*-

"""
Created by jianbing on 2017-10-30
"""
import logging.handlers
import sys

log = logging.getLogger()
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s -- %(module)s '
                                               '-- %(lineno)s -- %(message)s'))

if console_handler not in log.handlers:
    log.addHandler(console_handler)


# def debug(msg):
#     _logger.debug("DEBUG " + str(msg))
#
#
# def info(msg):
#     _logger.info(Fore.GREEN + "INFO " + str(msg) + Style.RESET_ALL)
#
#
# def error(msg):
#     _logger.error(Fore.RED + "ERROR " + str(msg) + Style.RESET_ALL)
#
#
# def warn(msg):
#     _logger.warning(Fore.YELLOW + "WARNING " + str(msg) + Style.RESET_ALL)
