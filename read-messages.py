from datetime import datetime
from datetime import timedelta
import csv
import json
import time

message_counts = {}

recipients = ['aditya', 'alice', 'amal', 'christopher', 'edridge', 'grace', 'kavin', 'phillip', 'raghav', 'sajid', 'sangeetha', 'sarah', 'talitha', 'vishwa', 'yuliya']
# recipients = ['alice']

oldest_timestamp = int(time.time())
newest_timestamp = 0

for name in recipients:
	filename = 'messages/' + name + '_message.json'
	with open(filename) as f:
		data = json.load(f)
		for msg in data['messages']:
			stamp_msg = msg['timestamp_ms'] / 1000
			if stamp_msg < oldest_timestamp:
				oldest_timestamp = stamp_msg
			if stamp_msg > newest_timestamp:
				# print(stamp_msg)
				newest_timestamp = stamp_msg

oldest_timestamp_datetime = datetime.utcfromtimestamp(oldest_timestamp)
# oldest_timestamp_datetime = datetime.strptime('7 Aug 2018 4:00AM', '%d %b %Y %I:%M%p')

newest_timestamp_datetime = datetime.utcfromtimestamp(newest_timestamp)
# newest_timestamp_datetime = datetime.strptime('11 Aug 2018 5:00AM', '%d %b %Y %I:%M%p')

for name in recipients:
	filename = 'messages/' + name + '_message.json'
	with open(filename) as f:
		data = json.load(f)
		messages_unordered = data["messages"]
		messages_sorted = sorted(messages_unordered, key=lambda message: message["timestamp_ms"])

		window_size = timedelta(hours=12)

		prev_window_open = oldest_timestamp_datetime
		prev_window_close = prev_window_open + window_size

		messages_sorted.reverse()
		cur_timestamp = datetime.utcfromtimestamp(int(messages_sorted.pop()["timestamp_ms"] / 1000))
		count = 0
		while prev_window_close < newest_timestamp_datetime:
			if len(messages_sorted) > 0:
				if cur_timestamp >= prev_window_open and cur_timestamp < prev_window_close:
					count += 1
					cur_timestamp = datetime.utcfromtimestamp(int(messages_sorted.pop()["timestamp_ms"] / 1000))
				else:
					if cur_timestamp < prev_window_open:
						count += 1
						cur_timestamp = datetime.utcfromtimestamp(int(messages_sorted.pop()["timestamp_ms"] / 1000))
					elif prev_window_close in message_counts:
						message_counts[prev_window_close].append(count)
						prev_window_open = prev_window_close
						prev_window_close = prev_window_open + window_size
					else:
						message_counts[prev_window_close] = [count]
						prev_window_open = prev_window_close
						prev_window_close = prev_window_open + window_size
			else:
				if cur_timestamp >= prev_window_open and cur_timestamp < prev_window_close:
					count += 1
					cur_timestamp = newest_timestamp_datetime + timedelta(days=10)
				else:
					if prev_window_close in message_counts:
							message_counts[prev_window_close].append(count)
					else:
						message_counts[prev_window_close] = [count]
					prev_window_open = prev_window_close
					prev_window_close = prev_window_open + window_size
		# if prev_window_close in message_counts:
		# 	message_counts[prev_window_close].append(count)
		# else:
		# 	message_counts[prev_window_close] = [count]

for window, counts in message_counts.items():
	if len(counts) != len(recipients):
		print(window)
		print(counts)
		raise Exception("Fucked up!")

with open('message_windows.csv', 'wb') as msg_counts:
	writer = csv.writer(msg_counts, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['window_close'] + recipients)
	for windows, counts in sorted(message_counts.items()):
		writer.writerow([windows - timedelta(hours=5)] + counts)
