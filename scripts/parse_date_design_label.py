import re
from settings import seas_dict


def parse_the_labels(label,pub_name):

		my_date = None
		day = None
		year = None
		month = None
		issue = None
		volume = None
		season = None
		number = None
		month_string = None
		month_number = None
		day = "01"
		flag_season = False
		flag_month = True

		try:
			year_list = re.findall(r"\d\d\d\d", label)
			if len(year_list) == 1:
				year = year_list[0].lstrip(" ").rstrip(" ")
			else:
				year = year_list[-1].lstrip(" ").rstrip(" ")
		except Exception as e:
			print(str(e))
			quit()
		try:
			month_day= re.findall(r"\d{1,2}",label.split(year)[-1])
			if len(month_day) == 2:
				month_number = month_day[-2]
				day = month_day[-1]
			elif len(month_day) == 1:
				month_number = month_day[-1]
			# print(month_number)
			# print(int(month))
			# print(month)
			r = range(1,13)
			l = [*r]

			if not int(month_number) in l:
				# print(month)
				# print(l)
				# print("no manth here")
				month_number = None
				day = None
			#print(month)


		except Exception as e:
			#print(str(e))
			pass

		try:
			#print("finding issue")
			issue = re.findall(r"iss[.](\d{1,2})", label)[0].lstrip(" ").rstrip(" ")
			#print(issue)
		except:
			pass
		try:
			#print("finding number")
			number = re.findall(r"no[.](\d{1,2})", label)[0].lstrip(" ").rstrip(" ")
			#print(number)
		except:
			pass


		try:
			#print('fining volume')
			volume = re.findall(r"v[.](\d{1,2})", label)[0].lstrip(" ").rstrip(" ")
			#print(volume)
		except:
			pass
		try:
			month_string = re.findall(r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)", label)[0].lstrip(" ").rstrip(" ")
			try: 
				day = my_label.split(month_string)[-1]
			except:
				pass
		except:
			pass
		try:
			#print("here")
			season = re.findall(r"Spring|spring|Summer|summer|Autumn|autumn|Winter|winter", label)[0].lstrip(" ").rstrip(" ")
			#print(season)
		except Exception as e:

			#print(str(e))
			pass


		if year and month_number:
			#print("yera and moth")
			my_date = "{} {} {}".format(year, month_number, day)
		elif year and month_string:
			my_date = "{} {} {}".format(year, month_string, day)
		elif season:
			month_string = seas_dict[season]
			my_date = "{} {} {}".format(year, month_string, day)
			flag_season = True
		else:
			month_number = "01"
			my_date = "{} {} {}".format(year, month_number, day)
			flag_month = True

		return (my_date, volume, issue,  number,season, month_string, month_number, year, flag_season, flag_month)