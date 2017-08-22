#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8

import json
import logging
import os
import random
import re
import sys
import time
import stat
import argparse

import zbxtg_settings as cfg
from lib.tg import TelegramAPI
from lib.zbx import ZabbixAPI

example_message = """
Base-Source: https://github.com/ableev/Zabbix-in-Telegram/
Example:
./zbxtg_send.py --username "username" --message "coolmessage" --subject "wazzup" --debug
./zbxtg_send.py --message "coolmessage" --subject "wazzup" --type group --groupname "zzz" --debug
TBD
#./zbxtg_send.py --username "username" --message "coolmessage" --subject "wazzup" --type group --debug
"""
log = logging.getLogger("zbxtg")


def parse_cli_args(_args=None):
    usage_string = './zbxtg_send.py [-h] <ARG> ...'

    parser = argparse.ArgumentParser(
      description=example_message,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      usage=usage_string
    )

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug')
    parser.add_argument('--username', dest='tg_username', type=str,
                        help='username')
    parser.add_argument('--message', dest='msg_body', type=str,
                        default="",
                        help='')
    parser.add_argument('--subject',
                        type=str,
                        dest='msg_subject',
                        help='')
    parser.add_argument('--type', type=str, dest="tg_type",
                        default="private",
                        help='TODO: wtf channel|group|supergroup')
    parser.add_argument('--groupname', dest='tg_groupname',
                        type=str,
                        help='If not passed - will be fetched from config')
    parser.add_argument('--disable_notification', action='store_true',
                        default=False,
                        dest="disable_notification",
                        help='Send silent message')
    parser.add_argument('--disable_web_page_preview', action='store_true',
                        default=False,
                        dest="disable_web_page_preview",
                        help='')
    parser.add_argument('--markdown', action='store_true',
                        default=False,
                        dest="markdown",
                        help='')
    parser.add_argument('--html', action='store_true',
                        default=False,
                        dest="html",
                        help='')
    parser.add_argument('--send-file', type=str,
                        dest="send_file",
                        help='')

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(args=_args)


def main():

    tmp_dir = cfg.zbx_tg_tmp_dir

    lformat = logging.Formatter(
        '%(asctime)-15s [%(name)-5s][%(levelname)-8s] %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(lformat)
    log.setLevel(logging.INFO)
    log.addHandler(ch)

    if not os.path.isdir(tmp_dir):
        log.debug("Tmp dir doesn't exist, creating new one...")
        os.makedirs(tmp_dir)
        log.debug("Using {0} as a temporary dir".format(tmp_dir))

    if args.debug:
        fh = logging.FileHandler(cfg.log_file)
        fh.setFormatter(lformat)
        log.setLevel(logging.DEBUG)
        log.addHandler(fh)

    tg = TelegramAPI(key=cfg.tg_key)
    tg.type = args.tg_type
    if not tg.get_me()['ok']:
        log.error("Something wrong with bot config! %s" % tg.get_me())
        sys.exit(1)
    tg.tmp_uids_file = os.path.join(tmp_dir, "uids.txt")
    tg.disable_notification = args.disable_notification
    tg.disable_web_page_preview = args.disable_web_page_preview
    tg.markdown = args.markdown
    tg.html = args.html
    if hasattr(cfg, "emoji_map"):
        tg.emoji_map = cfg.emoji_map

    if tg.type != "private" and not args.tg_groupname:
        log.warning("No group-name passed."
                    "Using defaut:{}".format(cfg.tg_group_default))
        zbx_to = cfg.tg_group_default

    ### End of pre-configure
    log.debug("Start notify process")
    uid = tg.get_uid(args.tg_username)

    tg_mesage = (args.msg_subject + "\n" + args.msg_body)
    # add signature, turned off by default, you can turn it on in config
    if cfg.zbx_tg_signature:
        tg_mesage.append("--\n{}".format(cfg.zbx_tg_signature))

    log.debug("Send message:")
    if args.send_file:
        result = tg.send_photo(uid, tg_mesage, args.send_file)
    else:
        result = tg.send_message(uid, tg_mesage)

    if not result["ok"]:
        log.error("Failed to send message")
        sys.exit(1)

    # log.debug("Getting zabbix..")
    #
    # zbx = ZabbixAPI(server=cfg.zbx_server, username=cfg.zbx_api_user,
    #                 password=cfg.zbx_api_pass)
    # zbx.login()
    # zbx_graph = cfg.zabbix_pic
    # zbxtg_file_img = zbx.graph_get(zbx_graph["itemid"],
    #                                zbx_graph["image_period"],
    #                                zbx_graph["title"],
    #                                zbx_graph["image_width"],
    #                                zbx_graph["image_height"], tmp_dir)
    # import ipdb;ipdb.set_trace()
    # sys.exit(1)


if __name__ == "__main__":
    print ("ZZ:{}".format(sys.argv[0:]))
    args = parse_cli_args()
    main()
