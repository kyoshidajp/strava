#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    jognote2strava.py

    Transfer from Jognote(http://www.jognote.com) data
    to Strava(http://www.strava.com).
"""
from jognote import Jognote, Workout
from strava import Strava
import optparse
import logging
from datetime import datetime
import sys

__author__ = 'kyoshidajp <claddvd@gmail.com>'

# post setting
COUNTRY = 'Japan'
START_TIME = '00:00:00'
LOCATION = 'Yokohama'
TITLE_PREFIX = '[jognote] '


def get_opt():
    """
    Parse command line option
    """
    parser = optparse.OptionParser()

    # jognote id
    parser.add_option ('-i', '--jognote_id',
                       dest = 'jognote_id',
                       help = 'Login ID at JogNote. Cannot use OpenID\'s password.'
                       )
    # jognote password
    parser.add_option ('-p', '--jognote_password',
                       dest = 'jognote_password',
                       help = 'Login password at JogNote. Cannot use OpenID\'s password.'
                       )
    # export start date at jognote
    parser.add_option ('-s', '--startdate',
                       dest = 'start_date',
                       help = 'Start date of export. Input yyyy/mm. ex) 2010/01'
                       )
    # export end date at jognote
    parser.add_option ('-e', '--enddate',
                       dest = 'end_date',
                       help = 'End date of export. Input yyyy/mm. ex) 2011/12'
                       )
    # strava email
    parser.add_option ('-m', '--strava_email',
                       dest = 'strava_email',
                       help = 'Login email at Strava. Cannot use OpenID\'s password.'
                       )
    # strava password
    parser.add_option ('-q', '--strava_password',
                       dest = 'strava_password',
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

def init_log(level = logging.INFO):
    """
    Logging setting
    """

    try:
        format = '[%(levelname)s] %(message)s'
        logging.basicConfig(level=level, format=format)
    except ValueError:
        logging.error('Incorrect log level.')
        sys.exit()

def get_type_name(name):
    """
    Get strava type name from Workout Object

    name is workout index of Workout Object.
    """
    
    workout_type = [ 'Run', 'Swim', 'Ride', 'Walk']
    if len(workout_type) < name:
        logging.error('Incorrect workout name.')
        return False

    return workout_type[name]


# parse command line option
options = get_opt()
jognote_id = options.jognote_id
jognote_password = options.jognote_password
start_date = options.start_date
end_date = options.end_date
strava_email = options.strava_email
strava_password = options.strava_password
log_level = options.log_level

# set log settings
init_log(log_level)

# get jognote data
jog = Jognote(jognote_id, jognote_password, start_date, end_date, log_level)
history = jog.export()
logging.debug('%d data export from JogNote' % len(history))

# make strava object
strava = Strava(strava_email, strava_password, log_level)

for workout in history:
    name = get_type_name(workout.name)
    start_date = workout.date.strftime('%m/%d/%Y')
    title = '%s%s' % (TITLE_PREFIX, start_date)
    elapsed_time = ':'.join(list(workout.time))
    distance = workout.distance

    # post data
    strava.add_activity(name, title, COUNTRY, LOCATION,
                        start_date, START_TIME, elapsed_time,
                        distance)
