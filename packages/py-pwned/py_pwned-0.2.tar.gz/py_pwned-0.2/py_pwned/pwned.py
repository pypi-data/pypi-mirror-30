import json
import os
import sys
import logging

from time import sleep

import hashlib

from getpass import getpass
from validate_email import validate_email

import cfscrape


class PwNed:

    def __init__(self):
        try:
            self.pwnedlist = []
            self.breachlist = []
            self.breachrawdata = []
            self.breachdata = []
            self.sleeptime = 2
            self.headers = {'User-Agent': 'My Little Python Script'}

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def searchpwd(self, pwd=''):
        try:
            while pwd is '':
                pwd = getpass("What password should I search for : ")

            #create half a password to show later
            l = len(pwd)
            pwd_p = pwd[:3] + "*"*(l-3)

            # Before sending it over the line, hash the pwd!!
            sha_1 = hashlib.sha1()
            pwd = pwd.encode('utf-8')
            sha_1.update(pwd)
            sha1pwd = sha_1.hexdigest()

            url = "https://api.pwnedpasswords.com/pwnedpassword/{}".format(sha1pwd)
            scraper = cfscrape.create_scraper()

            r = scraper.get(url, headers=self.headers)
            sleep(self.sleeptime)  # this just to secure that user is not over using the API!
            if r.status_code == 200:
                if r.content is not None and len(r.content) > 0:

                    self.breachrawdata.append(r.content)
                    self.breachdata.append([pwd_p, str(r.content)])

                    return self.breachdata
            elif r.status_code == 404:  # nothing found
                self.breachdata.append([pwd_p, 0])
                return self.breachdata

            return None

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            return None

    def searchemail(self, email=''):
        try:
            while not validate_email(email):
                email = input("What email should I search for : ")

            url = "https://haveibeenpwned.com/api/v2/breachedaccount/{}".format(email)
            scraper = cfscrape.create_scraper()

            r = scraper.get(url, headers=self.headers)
            sleep(self.sleeptime)  # this just to secure that user is not over using the API!
            if r.status_code == 200:
                if r.content is not None and len(r.content) > 0:
                    html = r.content

                    self.breachrawdata = json.loads(html.decode('utf-8'))
                    self.breachdata = self.getbreachdata(email, self.breachrawdata)

                    return self.breachdata

            return None

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            return None

    def getbreachdata(self, email, breaches=None):
        try:
            if breaches is None:
                return None

            self.pwnedlist = []
            for b in breaches:
                domain = b.get('Domain', '')
                if domain == "":
                    domain = b.get('Name', '')

                datum = b.get('BreachDate', '')
                data = [email, datum, domain]
                self.pwnedlist.append(data)
            return self.pwnedlist
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            return None

# IsActive
# IsRetired
# Title
# AddedDate
# IsFabricated
# Description
# PwnCount
# Name
