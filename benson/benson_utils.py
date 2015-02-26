__author__ = 'michaelmoliterno'

import csv
import dateutil.parser
import re
# import sys
#
import matplotlib.pyplot as plt
# import datetime

def get_MTA_data_by_turnstile(mta_file):

    try:
        mta_dict = {}

        with open(mta_file,'r') as turnstile_file:
            reader = csv.reader(turnstile_file)
            for num, row in enumerate(reader):

                # Skip header row (column names)
                if num == 0:
                    continue

                else:

                    # If the turnstile is not in the dictionary
                    if tuple(row[0:4]) not in mta_dict:

                        # Add the remaining columns to the dictionary; the key maps to a list of lists
                        mta_dict[tuple(row[0:4])] = [row[4:]]

                    # If the turnstile is in the dictionary
                    else:

                        # Append the remaining columns as a list to key's list of lists
                        mta_dict[tuple(row[0:4])].append(row[4:])
        return mta_dict

    except:
        print "could not process dictionary. please ensure you are using a \
        file from http://web.mta.info/developers/turnstile.html \
        from Oct 18 2014 or later."
        return None




def translate_station(x):

    """
    This is a function that translates the lines (if necessary). Sometimes the same station list lines as both ACJZ2345 and 2345ACJZ.
    I need to use the lines to uniquely ID the stations because, for example, there 5 unique '86 ST' stations,but they are all
    coded the same way in the MTA data.
    """
    return {
        'ACJZ2345': '2345ACJZ',
        'ACENQRS1237': '1237ACENQRS',
        'AC1' : '1AC',
        'JZ456' : '456JZ',
        'BDNQR2345' : '2345BDNQR',
        'ABCD1' : '1ABCD',
        'R2345' : '2345R',
        'LNQR456' : '456LNQR',
        'BD4' : '4BD',
        'ACENGRS1237': '1237ACENQRS'
    }[x]





def process_mta_data(mta_files):

    """
    This function will cleanse an array of MTA data
    TODO: add some try/except blocks to account for file not found or other I/O errors
    """

    ## This will hold the MTA data.  Each turnstile is a tuple that maps to
    ## a list of list of MTA data

    mta_time_series = {}

    ##This reads in the files
    ##I should have written a function to do this... maybe next time?
    for mtafile in mta_files:
        with open(mtafile,'r') as turnstile_file:
            reader = csv.reader(turnstile_file)
            for num, row in enumerate(reader):

                # This skips the header (column values)
                if num == 0:
                    continue

                else:

                    ## String manipulaton on the date and time values to move into a parsable format
                    dayarray = row[6].split('/')[2],row[6].split('/')[0],row[6].split('/')[1]
                    date_string = ''.join(dayarray)+re.sub(':','',row[7])
                    mta_datetime  = dateutil.parser.parse(date_string)

                    # This calls translate_station(), defined above, on lines that need to be renamed
                    if row[4] in ('ACJZ2345','ACENQRS1237','AC1','JZ456','BDNQR2345','ABCD1','R2345','LNQR456','BD4'):
                        row [4] = translate_station(row[4])

                    # If the turnstile is not in the dictionay,
                    if tuple(row[0:5]) not in mta_time_series:

                        # Add the list (datetime,cumulative volume) to the list
                        # I'm including the lines because we need them to uniquely ID the stations
                        mta_time_series[tuple(row[0:5])] = [[mta_datetime,row[9]]]

                    # If the tuple is in the dictionry, add to the list of lists
                    else:

                        # I'm including the lines because we need them to uniquely ID the stations
                        # Add the list (datetime,cumulative volume) to the list
                        mta_time_series[tuple(row[0:5])].append([mta_datetime,row[9]])
    return mta_time_series


## defining a function that processes the data (so it can be called later if necessary)
def process_mta_time_series(mta_time_series):

    mta_day_counts = {}
    # This will track what (and how much) data I cleansed.  Would be useful to know if there are "faulty" turnstiles/stations.
    data_corrections_negatives = []
    data_omissions_too_large = []

    # For each turnstile
    for val in mta_time_series:

        # This will hold the time series for each turnstile
        date_count = {}

        # For each (datetime,cumulatative count) for each turnstile
        for x in mta_time_series[val]:

            # If the date HAS NOT been added to the dict, add the date as the key and the cumulative volume as the val
            if x[0].date() not in date_count:
                date_count[x[0].date()] = [x[1]]

            # If the date HAS been added to the dict, add the date as the key and the cumulative volume as the val
            else:
                date_count[x[0].date()].append(x[1])

        # For each date in the dict
        for d in date_count:

            # I settled on volume as the last count in the day minus the first counf in the day (the list is orderd)
            # Another option is volume = int(max(date_count[d]))-int(min(date_count[d]))
            volume = int(date_count[d][-1]) - int(date_count[d][0])

            ## Assuming negative counts are accurate, but negative. Seemed generally reasonable based on analysis of data.
            ## Values that are way too large will be ignore in the next step.
            if volume < 0:
                data_corrections_negatives.append([val,d,volume])
                volume = abs(volume)

            # I inspected the data and saw that the highest legitimate daily turnstile volumes are ~8000 (even for Penn/Grant Cent)
            # Anything over if very likely not valid, so I'm ignoring it
            if volume > 25000:
                data_omissions_too_large.append([val,d,volume])
                volume = 0

            ## Now, build the dict for each turnstile that maps to a list of (days,volumes)
            if val not in mta_day_counts:
                mta_day_counts[val] = [[d,volume]]
            else:
                mta_day_counts[val].append([d,volume])

    # Realizing now it might have made sense to make this a class since this is a silly way to return data...
    return mta_day_counts, data_corrections_negatives, data_omissions_too_large


def collapse_turns_to_cas(mta_day_counts):

    # substation = C/A
    substation_volume = {}

    for substation in mta_day_counts:

        ## Combining C/A, UNIT and STATION; also adding lines b/c they are needed to uniquely ID data
        station = substation[3]+" "+substation[1]+" "+substation[0]+" "+substation[4]

        for day in mta_day_counts[substation]:

            if tuple([station,day[0]]) not in substation_volume:
                substation_volume[tuple([station,day[0]])] = day[1]
            else:
                substation_volume[tuple([station,day[0]])] += day[1]

    return substation_volume

# This is a data cleaning function...self explanatory
# Rolling stations up into same station; sometimes the day makes stations look unique when they are the same
# This is string manipulation, which is bad... maybe should have been done in an earlier function.
def station_translate(x):
    return {
        'JAY ST-METROTEC: R': 'JAY ST-METROTEC: ACFR',
        'JAY ST-METROTEC: ACF': 'JAY ST-METROTEC: ACFR',
        'CHAMBERS ST: ACE23' : 'CHAMBERS ST: 123ACE',
        'CHAMBERS ST: 123' : 'CHAMBERS ST: 123ACE',
        '34 ST-PENN STA: ACE' : '34 ST-PENN STA: 123ACE',
        '34 ST-PENN STA: 123' : '34 ST-PENN STA: 123ACE'
    }[x]

def collapse_turns_to_stations(mta_day_counts):
    station_volume = {}

    # For each C/A per station
    for substation in mta_day_counts:

        #Using station name and line to define unique stations
        station = substation[3]+": "+substation[4]

        # If the station needs to be translated
        if station in ('JAY ST-METROTEC: R','JAY ST-METROTEC: ACF','CHAMBERS ST: ACE23','CHAMBERS ST: 123','34 ST-PENN STA: ACE','34 ST-PENN STA: 123'):
            station = station_translate(station)

        ## For each day
        for day in mta_day_counts[substation]:

            ## Build the dictionary
            if tuple([station,day[0]]) not in station_volume:
                station_volume[tuple([station,day[0]])] = day[1]
            else:
                station_volume[tuple([station,day[0]])] += day[1]

    return station_volume


def PlotStationVolumeWithAverages(station_volume,station):
    station_vals = []
    for x in station_volume:
        if x[0] == 'PELHAM PARKWAY: 25':
            station_vals.append([x[1], station_volume[x]])

    weekend_vals = []
    weekday_vals = []

    for key, val in station_vals:

        if key.weekday() >= 5:
            weekend_vals.append(val)
        else:
            weekday_vals.append(val)

    plt.title(station)
    plt.xlabel('Date')
    plt.ylabel('Passenger Volume')
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.xticks(rotation=45)
    plt.plot(*zip(*sorted(station_vals)))
    plt.axhline(y=sum(weekday_vals)/float(len(weekday_vals)), linewidth=2, color = 'k')
    plt.axhline(y=sum(weekend_vals)/float(len(weekend_vals)), linewidth=2, color = 'k')



def GetTotalVolume(station_volume):
    total_volume = {}
    for x in station_volume:
        if x[0] not in total_volume:
            total_volume[x[0]] = station_volume[x]
        else:
            total_volume[x[0]] += station_volume[x]
    return total_volume


def main_Benson(mta_files):

    mta_time_series = process_mta_data(mta_files)
    mta_day_counts, corrected_negatvies, omitted_too_large = process_mta_time_series(mta_time_series)

    print 'Negatives count: ',len(corrected_negatvies)
    print 'Omissions count: ',len(omitted_too_large)


    station_volume = collapse_turns_to_stations(mta_day_counts)
    total_volume = GetTotalVolume(station_volume)

    print len(mta_day_counts.keys()), "turnstiles in the data set"
    print len(total_volume.keys()), "stations in the dataset"