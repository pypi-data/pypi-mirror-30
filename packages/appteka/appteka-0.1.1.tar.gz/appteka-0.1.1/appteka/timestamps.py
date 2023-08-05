# appteka - helpers collection

# Copyright (C) 2018 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import datetime

def detect_fmt(s):
    """ Attempt top detect format of timestamp. """
    # TODO: this is stub
    if " " in s:
        return "date_time"
    else:
        return "secs_dot"

def convert_timestamp(s, fmt):
    """ 
    Convert string to timestamp in accordance with some format. 

    Parameters
    ----------
    s : str
        Some string representation of date-time.
    fmt : str
        Format of string. Supported formats: 
        - "secs_dot" (for example "1505314800.40")
        - "date_time" (for example "31/10/2017 16:30:00.000" or "12.07.2017 21:00:00.160000")

    Returns
    -------
    t : float
        Seconds since the epoch.
    
    """
    # TODO: [3] support format used in data base
    if fmt == "secs_dot":
        parts = s.split(".")
        a = parts[0]
        b = parts[1]
        if len(b) == 2:
            b = '0' + b
        v = float(a + '.' + b)
        return v
    elif fmt == "date_time":
        splitted = s.replace("/", " ").replace(":", " ").replace(".", " ").split()
        secs = datetime.datetime(
            int(splitted[2]), # year
            int(splitted[1]), # month
            int(splitted[0]), # day
            int(splitted[3]), # hours
            int(splitted[4]), # minutes
            int(splitted[5])  # secomds
        ).timestamp()
        return secs + float("0."+splitted[6]) # milliseconds
    else:
        return None

def get_time(secs, scale="s"):
    """ 
    Return time from timestamp. 

    Parameters
    ----------
    secs : float
        Seconds since the epoch.
    scale : str 
        Scale. Possible values: "ms" (milliseconds), "s" (seconds), "m" (minutes), "h" (hours).

    Returns
    -------
    label : str
        String label representing the time.
        
    """
    t = time.gmtime(secs)
    if   scale == "s":
        return time.strftime("%H:%M:%S", t)
    elif scale == "m":
        return time.strftime("%H:%M", t) 
    elif scale == "h":
        return time.strftime("%H", t)
    elif scale == "ms":
        ms = int(1000*(secs - int(secs)))
        return time.strftime("%H:%M:%S", secs) + ".{}".format(ms)
    
def get_date(secs):
    """ 
    Return date from timestamp. 

    Parameters
    ----------
    secs : float
        Seconds since the epoch.

    Returns
    -------
    Returns
    -------
    label : str
        String label representing the date.
    
    """
    t = time.gmtime(secs)
    return time.strftime("%y-%m-%d", t)
