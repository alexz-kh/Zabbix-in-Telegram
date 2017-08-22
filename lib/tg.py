# -*- coding: utf-8 -*-
import requests
import json
import os
import logging
import sys
"""
Source: https://github.com/ableev/Zabbix-in-Telegram/
"""

log = logging.getLogger("zbxtg")


class TelegramAPI():
    api_url = "https://api.telegram.org/bot"

    def __init__(self, key=None):
        if not key:
            log.error("No api key has been passed!")
            sys.exit(1)
        self.key = key
        self.proxies = {}
        # 'private' for private chats or 'group' for group chats
        self.type = "private"
        self.markdown = False
        self.html = False
        self.disable_web_page_preview = False
        self.disable_notification = False
        self.reply_to_message_id = 0
        self.tmp_uids_file = None
        self.emoji_map = None

    def http_get(self, url):
        res = requests.get(url, proxies=self.proxies)
        answer = res.text
        answer_json = json.loads(answer.decode('utf8'))
        return answer_json

    def get_me(self):
        url = self.api_url + self.key + "/getMe"
        me = self.http_get(url)
        return me

    def get_updates(self):
        url = self.api_url + self.key + "/getUpdates"
        log.debug("get_updates url:%s" % url)
        updates = self.http_get(url)
        log.debug("Content of /getUpdates: %s", updates)
        if not updates["ok"]:
            log.error(updates)
            sys.exit(1)
        else:
            return updates

    def process_emoji(self,message):
        """
        replace {{}} text with emojis
        """
        emoji_message = []
        for l in message.splitlines():
            l_new = l
            for k, v in self.emoji_map.iteritems():
                l_new = l_new.replace("{{" + k + "}}", v)
            emoji_message.append(l_new)
        return "\n".join(emoji_message)

    def send_message(self, to, message):
        url = self.api_url + self.key + "/sendMessage"
        if self.emoji_map:
            message = self.process_emoji(message)
        params = {"chat_id": to, "text": message,
                  "disable_web_page_preview": self.disable_web_page_preview,
                  "disable_notification": self.disable_notification}
        if self.reply_to_message_id:
            params["reply_to_message_id"] = self.reply_to_message_id
        if self.markdown or self.html:
            parse_mode = "HTML"
            if self.markdown:
                parse_mode = "Markdown"
            params["parse_mode"] = parse_mode
        log.debug("Trying to /sendMessage:")
        log.debug("sendMessage url %s" % url)
        log.debug("post params: " + str(params))
        log.info("Sending message %s", params)
        res = requests.post(url, params=params, proxies=self.proxies)
        answer = res.text
        answer_json = json.loads(answer.decode('utf8'))
        log.info("Receive message %s", answer_json)
        if not answer_json["ok"]:
            log.error(answer_json)
            return answer_json
        else:
            return answer_json

    def send_photo(self, to, message, path):
        url = self.api_url + self.key + "/sendPhoto"
        if self.emoji_map:
            message = self.process_emoji(message)
        params = {"chat_id": to,
                  "caption": message,
                  "disable_notification": self.disable_notification}
        if self.reply_to_message_id:
            params["reply_to_message_id"] = self.reply_to_message_id
        files = {"photo": open(path, 'rb')}
        log.debug("Trying to /sendPhoto:")
        log.debug("Url:%s" % url)
        log.debug("Params:%s" % params)
        log.debug("files: " + str(files))
        log.info("Sending message %s", params)
        res = requests.post(
            url, params=params, files=files, proxies=self.proxies)
        answer = res.text
        answer_json = json.loads(answer.decode('utf8'))
        log.info("Receive message %s", answer_json)
        if not answer_json["ok"]:
            log.error(answer_json)
            return answer_json
        else:
            return answer_json

    def get_uid(self, name):
        """
        :param name:
        :return:
        """
        #uid = self.get_uid_from_cache(name)
        uid =False
        if not uid:
            uid = self.get_uid_from_updates(name)
        return uid

    def get_uid_from_updates(self, name):
        uid = False
        log.debug("Getting uid from /getUpdates...")
        updates = self.get_updates()
        if not len(updates["result"]):
            self.error_need_to_contact(name)
        for m in updates["result"]:
            if "message" in m:
                chat = m["message"]["chat"]
            elif "edited_message" in m:
                chat = m["edited_message"]["chat"]
            if chat["type"] == self.type == "private":
                if "username" in chat:
                    if chat["username"] == name:
                        uid = chat["id"]
            if (chat["type"] == "group" or chat[
                "type"] == "supergroup") and self.type == "group":
                if "title" in chat:
                    if chat["title"] == name.decode("utf-8"):
                        uid = chat["id"]
        if uid:
            log.debug("Sucesfully get {} <==> uid:{}".format(name,uid))
        self.update_cache_uid(name, uid)
        return uid

    def error_need_to_contact(self, to):
        botname=self.get_me()["result"]["username"]
        if self.type == "private":
            log.info("User '{0}' needs to send some "
                     "text bot:{1}in private".format(to, botname))
        if self.type == "group":
            log.info("You need to mention your bot:{0} in '{1}' "
                     "group chat (i.e. type @{0})".format(botname,to))
        sys.exit(1)

    def update_cache_uid(self, name, uid):
        cache_string = "{0};{1};{2}".format(name, self.type, str(uid).rstrip())
        log.debug("{0}: {1} >> {2}".format("Adding", cache_string,
                                                       self.tmp_uids_file))
        with open(self.tmp_uids_file, "a") as cache_file_uids:
            cache_file_uids.write(cache_string + "\n")

    def get_uid_from_cache(self, name):
        uid = False
        if os.path.isfile(self.tmp_uids_file):
            with open(self.tmp_uids_file, 'r') as cache_file_uids:
                cache_uids_old = cache_file_uids.readlines()
            for u in cache_uids_old:
                if name == u.split(";")[0] and self.type == u.split(";")[1]:
                    uid = u.split(";")[2]
                log.debug("Found user:{} id:{} in cache_file"
                          ":{}".format(name, uid, self.tmp_uids_file))

        return uid
