import sys
import traceback
import time

def a():
	exc_info = None
	try:
		time.sleep(9999)
	except:
		exc_info = sys.exc_info()
	return exc_info

e = a()
traceback.print_exception(*e)
for line in traceback.format_exception(*e):
	print line

