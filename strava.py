#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    strava.py

    Library for Strava(http://www.strava.com).

"""

from bs4 import BeautifulSoup
import mechanize
from datetime import datetime
import cookielib
import re
import sys
import time
import logging
import optparse

__author__ = 'kyoshidajp <claddvd@gmail.com>'


class Strava(object):
    """
    Strava Class
    """

    def __init__(self, email, password,
                 log_level=logging.WARNING):

        self.TOP_URL = 'http://www.strava.com'
        self.TOP_APP_URL = 'http://app.strava.com'
        self.EXPORT_START_DATE = '2011/01'
        self.date_format = '%Y/%m'
        self.today = datetime.now()

        # sleep time
        self.__SLEEP_TIME = 2

        self.init_log(log_level)

        self.email, self.password = self.get_account(email, password)
        self.browser = self.make_browser()

        # login
        self.login()

    def get_account(self, email, password):
        """
        Setting for login account
        """

        if not (email and password):
            logging.error('Email or password is incorrect.')
            sys.exit()

        return (email, password)

    def login(self):
        """
        Login service
        """

        https_top_url = re.compile('^http').sub('https', self.TOP_URL)
        self.browser.open('%s/login' % https_top_url)
        self.browser.select_form(nr=0)
        self.browser.form['email'] = self.email
        self.browser.form['password'] = self.password
        self.browser.submit()

        url = self.browser.geturl()

        login_correct_re = re.compile(r'^%s/dashboard$' % self.TOP_APP_URL)
        if not login_correct_re.match(url):
            logging.error('Failed to login. Check your email and password.')
            sys.exit()

    def make_browser(self):
        """
        Make emulation browser
        """
        browser = mechanize.Browser()

        cj = cookielib.LWPCookieJar()
        browser.set_cookiejar(cj)

        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),
                                   max_time=1)

        browser.addheaders = [('User-agent',
                              ('Mozilla/5.0 (Windows; U; Windows NT 5.1; rv:1.7.3)'
                               ' Gecko/20041001 Firefox/0.10.1'))]
        return browser

    def delete_activities(self):
        """
        Delete activities
        """

        delete_param = '_method=delete'
        delete_correct_re = re.compile(r'^%s/athlete/training$'
            % self.TOP_APP_URL)

        self.browser.open('%s/dashboard?feed_type=my_activity'
            % self.TOP_APP_URL)
        body = self.browser.response().read()
        soup = BeautifulSoup(body)
        alink_list = soup.findAll('a', href=re.compile(r'^/activities/\d+?$'))

        if len(alink_list) == 0:
            # deleted all activities
            return

        for alink in alink_list:

            if alink['class'][0] == 'activity-map':
                continue

            uri = alink['href']
            logging.debug('Delete %s', uri)
            self.browser.open('%s%s' % (self.TOP_APP_URL, uri), delete_param)
            url = self.browser.geturl()
            if not delete_correct_re.match(url):
                logging.error('Failed to delete. %s' % uri)

            # sleeping...
            time.sleep(self.__SLEEP_TIME)

        # recursive while activities link
        return self.delete_activities()

    def add_activity(self, activity_type, activity_name, 
                     activity_country, activity_location,
                     activity_start_date, activity_start_time_of_day,
                     activity_elapsed_time, activity_distance):
        """
        Add an activity manually
        """

        if not all((activity_type and activity_name and activity_country
            and activity_location and activity_start_date 
            and activity_start_time_of_day, activity_elapsed_time
            and activity_distance)):
            logging.error('Failed to add activity. Check data.')
            return

        self.browser.open('%s/activities/new' % self.TOP_URL)
        self.browser.select_form(nr=0)
        self.browser.form['activity[type]'] = [activity_type]
        self.browser.form['activity[name]'] = activity_name
        self.browser.form['activity[country]'] = [activity_country]
        self.browser.form['activity[input_location]'] = activity_location
        self.browser.form['activity[start_date]'] = activity_start_date
        self.browser.form['activity[start_time_of_day]'] = activity_start_time_of_day
        self.browser.form['activity[elapsed_time]'] = activity_elapsed_time
        self.browser.form['activity[distance]'] = str(activity_distance)

        logging.debug(' '.join((activity_type, activity_name, activity_country,
                      activity_location, activity_start_date,
                      activity_start_time_of_day, activity_elapsed_time,
                      activity_distance)))
        self.browser.submit()

        url = self.browser.geturl()
        activities_re = re.compile(r'^%s/activities/(\d+?)$' % self.TOP_APP_URL)
        if not activities_re.match(url):
            logging.error('Failed to add an activity. %s'
                % activity_start_date)
            if not force:
                sys.exit()

        # sleeping...
        time.sleep(self.__SLEEP_TIME)

    def init_log(self, level):
        """
        Logging setting
        """

        try:
            format = '[%(levelname)s] %(message)s'
            logging.basicConfig(level=level, format=format)
        except ValueError:
            logging.error('Log level is incorrect.')
            sys.exit()


def get_opt():
    """
    Command line option
    """
    parser = optparse.OptionParser()

    # email
    parser.add_option ('-e', '--email',
                       dest = 'email',
                       help = 'Login email at Strava. Cannot use OpenID\'s password.'
                       )
    # password
    parser.add_option ('-p', '--password',
                       dest = 'password',
                       help = 'Login password at Strava. Cannot use OpenID\'s password.'
                       )
    # log level 
    parser.add_option ('-l', '--loglevel',
                       dest = 'log_level',
                       default = 'WARNING',
                       help = 'Log level'
                       )
    options, remainder = parser.parse_args()
    return options

if __name__ == '__main__':

    # parse command line option
    options = get_opt()
    email = options.email
    password = options.password

    strava = Strava(email, password, logging.DEBUG)

    # delete
    #strava.delete_activities()

    # add
    activity_type = 'Run'
    activity_country = 'Japan'
    activity_location = 'Yokohama'
    activity_start_date = '01/26/2013'
    activity_name = '%s %s' % (activity_type, activity_start_date)
    activity_start_time_of_day = '00:00:00'
    activity_elapsed_time = '01:00:00'
    activity_distance = '10'
    strava.add_activity(activity_type, activity_name, activity_country,
                        activity_location, activity_start_date,
                        activity_start_time_of_day, activity_elapsed_time,
                        activity_distance)
