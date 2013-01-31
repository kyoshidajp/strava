strava
======

Python library for Strava. Upload or delete activity data.

Upload activity data not required latitude, and longitude.

Delete activity is delete all your activities.

Requirements
------------
Using external library.

+   [mechanize](http://wwwsearch.sourceforge.net/mechanize/) 
+   [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
+   [jognote.py](https://github.com/kyoshidajp/jognote/blob/master/jognote.py)  
    Sorry you can't get jognote.py at pipy. Download (or checkout) that, and add your module search path.


Usage
------
### upload activities ###
    from strava import Strava
    strava = Strava(strava_email, strava_password)
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

### delete activities ###
Simple way is execute by command line.

    $ python strava.py -e strava_email -p strava_password

or

    from strava import Strava
    strava = Strava(strava_email, strava_password)
    strava.delete_activities()

