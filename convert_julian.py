#!/usr/bin/env python
u"""
convert_julian.py
Written by Tyler Sutterley (06/2017)

Return the calendar date and time given Julian date.

CALLING SEQUENCE:
	date_inp = convert_julian(julian)
	year = date_inp['year']
	month = np.int(date_inp['month'])
	day = date_inp['day']

INPUTS:
	JD: Julian Day of the specified calendar date.

OUTPUTS:
	month: Number of the desired month (1 = January, ..., 12 = December)
	day: Number of day of the month
	year: Number of the desired year
	hour: hour of the day
	minute: minute of the hour
	second: second (and fractions of a second) of the minute

OPTIONS:
	ASTYPE: convert output to variable type (e.g. int).  Default is float
	FORMAT: format of output coordinates
		'dict': dictionary with variable keys as listed above
		'tuple': tuple with variable order YEAR,MONTH,DAY,HOUR,MINUTE,SECOND
		'zip': aggregated variable sets

PYTHON DEPENDENCIES:
	numpy: Scientific Computing Tools For Python (http://www.numpy.org)

NOTES:
	Translated from caldat in "Numerical Recipes in C", by William H. Press,
		Brian P. Flannery, Saul A. Teukolsky, and William T. Vetterling.
		Cambridge University Press, 1988 (second printing).
	Hatcher, D. A., "Simple Formulae for Julian Day Numbers and Calendar Dates",
		Quarterly Journal of the Royal Astronomical Society, 25(1), 1984.

UPDATE HISTORY:
	Updated 06/2017: added option FORMAT to change the output variables format
	Updated 06/2016: added option to convert output to variable type (e.g. int)
	Updated 11/2015: extracting the values from singleton dimension cases
	Updated 03/2015: remove singleton dimensions if initially importing value
	Updated 03/2014: updated to be able to convert arrays
	Written 05/2013
"""

def convert_julian(julian, ASTYPE=None, FORMAT='dict'):
	import numpy as np

	#-- number of dates
	if (np.ndim(julian) == 0):
		n_dates = 1
	else:
		n_dates = len(julian)
	#-- allocate for each output variable
	hour = np.zeros((n_dates))
	minute = np.zeros((n_dates))
	second = np.zeros((n_dates))
	day = np.zeros((n_dates))
	month = np.zeros((n_dates))
	year = np.zeros((n_dates))

	#-- Beginning of Gregorian calendar
	igreg = 2299161.0
	#-- rounded julian
	jul = np.zeros((n_dates))
	jul[:] = np.floor(julian + .5)
	#-- residual
	f = np.zeros((n_dates))
	f[:] = julian + .5 - jul

	#-- number of points that contain hour, minute and seconds
	hms_count = np.count_nonzero(f != 0)
	if (hms_count != 0): #-- Get hours, minutes, seconds.
		#-- indices with HMS
		ind = np.nonzero(f != 0)
		hour[ind] = np.floor(f[ind] * 24.0)
		fm = np.copy(f[ind] - hour[ind]/24.0)
		minute[ind] = np.floor(fm*1440.0)
		second[ind] = (fm - minute[ind]/1440.0) * 86400.0

	#-- number of points greater than the gregorian beginning
	#-- the cross-over to the gregorian calendar produces this correction
	greg_count = np.count_nonzero(jul >= igreg)
	ja = np.copy(jul)
	if (greg_count != 0):
		ind = np.nonzero(jul >= igreg)
		jalpha = np.floor(((jul[ind] - 1867216.0) - 0.25) / 36524.25)
		ja[ind] = jul[ind] + 1.0 + jalpha - np.floor(0.25 * jalpha)

	jb = ja + 1524.0
	jc = np.floor(6680.0 + ((jb-2439870)-122.1)/365.25)
	jd = np.floor(365.0 * jc + (0.25 * jc))
	je = np.floor((jb - jd) / 30.6001)

	day[:] = jb - jd - np.floor(30.6001 * je)
	#-- calculating months
	month[:] = je -1
	#-- fixing months
	month_gt12 = np.count_nonzero(month > 12)
	if (month_gt12 != 0):
		ind = np.nonzero(month > 12)
		month[ind] = month[ind] - 12
	#-- calculating years
	year[:] = jc - 4715
	month_gt2 = np.count_nonzero(month > 2)
	if (month_gt2 != 0):
		ind = np.nonzero(month > 2)
		year[ind] = year[ind] - 1
	#-- fixing years
	year_lt0 = np.count_nonzero(year <= 0)
	if (year_lt0 != 0):
		ind = np.nonzero(year <= 0)
		year[ind] = year[ind] - 1

	#-- convert all variables to output type (from float)
	if ASTYPE is not None:
		year = year.astype(ASTYPE)
		month = month.astype(ASTYPE)
		day = day.astype(ASTYPE)
		hour = hour.astype(ASTYPE)
		minute = minute.astype(ASTYPE)
		second = second.astype(ASTYPE)

	#-- if only a single value was imported initially: remove singleton dims
	if (np.ndim(julian) == 0):
		year = year.item(0)
		month = month.item(0)
		day = day.item(0)
		hour = hour.item(0)
		minute = minute.item(0)
		second = second.item(0)

	#-- return date variables in output format (default python dictionary)
	if (FORMAT == 'dict'):
		return dict(year=year, month=month, day=day,
			hour=hour, minute=minute, second=second)
	elif (FORMAT == 'tuple'):
		return (year, month, day, hour, minute, second)
	elif (FORMAT == 'zip'):
		return zip(year, month, day, hour, minute, second)
