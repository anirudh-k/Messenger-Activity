from datetime import datetime
from datetime import timedelta
import csv
import json
import time

message_counts = {}

recipients = ['aditya', 'alice', 'amal', 'christopher', 'edridge', 'grace', 'kavin', 'phillip', 'raghav', 'sajid', 'sangeetha', 'sarah', 'talitha', 'vishwa', 'yuliya']

oldest_timestamp = int(time.time())

for name in recipients:
	filename = 'messages/' + name + '_message.json'
	with open(filename) as f:
		data = json.load(f)
		old_stamp_msg = int(data['messages'].pop()['timestamp_ms']) / 1000
		if old_stamp_msg < oldest_timestamp:
			oldest_timestamp = old_stamp_msg

oldest_timestamp_datetime = datetime.utcfromtimestamp(oldest_timestamp)
# oldest_timestamp_datetime = datetime.strptime('1 Sep 2015 12:00AM', '%d %b %Y %I:%M%p')
newest_timestamp = datetime.utcfromtimestamp(1535260101)

for name in recipients:
	filename = 'messages/' + name + '_message.json'
	with open(filename) as f:
		data = json.load(f)
		messages_unordered = data["messages"]
		messages_sorted = sorted(messages_unordered, key=lambda message: message["timestamp_ms"])

		window_size = timedelta(days=1)

		prev_window_open = oldest_timestamp_datetime
		prev_window_close = prev_window_open + window_size

		messages_sorted.reverse()
		cur_timestamp = datetime.utcfromtimestamp(int(messages_sorted.pop()["timestamp_ms"] / 1000))
		count = 0
		while prev_window_close < newest_timestamp:
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
					cur_timestamp = newest_timestamp + timedelta(days=10)
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
		writer.writerow([windows] + counts)