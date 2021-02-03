import sys
import os.path


class Database:
	def __init__(self):
		self.is_open = False

	def open(self, name):
		self.name = name
		self.config = open(self.name+'.config', 'r+')
		self.data = open(self.name+'.data', 'r+')
		self.is_open = True

	def close(self):
		self.config.close()
		self.data.close()
		self.is_open = False

def menu():
	print("\n============================")
	print("1: Create new database")
	print("2: Open database")
	print("3: Close database")
	print("4: Display record")
	print("5: Update record")
	print("6: Create report")
	print("7: Add record")
	print("8: Delete record")
	print("9: Quit")
	print("============================")

def main():
	database = Database()
	choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9",]
	while True:
		menu()
		choice = input("Please Enter a Command 1-9: ")

		while choice not in choices:
			choice = input("\nError: Please enter a correct command (1-9): ")

		if (choice == "1"):
			createNewDatabase()

		elif (choice == "2"):
			openDatabase(database)

		elif (choice == "3"):
			closeDatabase(database)

		elif (choice == "4"):
			displayRecord(database)

		elif (choice == "5"):
			updateRecord(database)
		elif (choice == "6"):
			createReport(database)
		elif (choice == "7"):
			addRecord(database)
		elif (choice == "8"):
			deleteRecord(database)
		elif (choice == "9"):
			deleteDatabase(database)
			print('Exiting Program...')
			break

#==================================================================
#
#              1) Create New Database
#
#==================================================================
def createNewDatabase():
	#Gets the csv file name to use as the database
	#---------------------------------------------
	filename = input("\nYou have chosen \"Create a new database\" Please enter the name of the csv file you would like to use: ")
	while (not os.path.isfile(filename+'.csv')):		#Continues until a correct file has been given
		filename = input("{}.csv was not found. Please enter a correct csv file: ".format(filename))
	print("\n{}.csv was successfully found!".format(filename))

	#Opens the file and intitializes the reader to 0,0
	#-------------------------------------------------
	source = open(filename+'.csv', 'r')
	source.seek(0,0)

	#Gets the field_names and number of fields
	#-----------------------------------------
	field_names = source.readline().rstrip('\n').split(',')
	fields = len(field_names)

	#Gets the size of each field
	#---------------------------
	field_sizes = [0 for i in range(fields)]
	num_records = 0
	for line in source:
		record = parseRecord(line)
		for idx, field in enumerate(record):
			if (len(field) > field_sizes[idx]):
				field_sizes[idx] = len(field)
		num_records += 1

	#Sets the Divider
	#----------------
	divider = '!'

	#Writes the num_records, fields, field_sizes, and divider into the config file
	#-----------------------------------------------------------------------------
	config = open(filename+'.config', 'w')
	config.write(str(num_records)+'\n')
	config.write(str(sum(field_sizes)+fields)+'\n')
	config.write(str(fields)+'\n')
	for idx in range(fields):
		config.write(field_names[idx]+' '+str(field_sizes[idx])+'\n')
	config.write(str(divider))
	config.close()

	#Writes the data into the data file
	#----------------------------------
	data = open(filename+'.data', 'w')
	source.seek(0,0)
	next(source)
	for line in source:
		record = parseRecord(line)
		for idx, entry in enumerate(record):
			data.write(entry)
			data.write(divider*(field_sizes[idx] - len(entry)))
			if (idx < (fields - 1)):
				data.write(divider)
		data.write('\n')
		data.write(divider*(sum(field_sizes) + fields - 1))
		data.write('\n')
	data.close()

	source.close()

#==================================================================
#
#              2) Open Database
#
#==================================================================
def openDatabase(database):
	#Gets the file name of the database to open
	#------------------------------------------
	filename = input("You have chosen \"Open a database\" Please enter the name of the database you would like to open: ")
	while ((not os.path.isfile(filename+'.data') or not os.path.isfile(filename+'.config')) and not filename == 'q'):		#Continues until a correct file has been given
		filename = input("{} was not found. Please enter a different database (or type \"q\" to exit): ".format(filename))
	if (filename == 'q'):
		print('Quitting...\n')
		return None

	database.open(filename)
	
	print("\n{} database was successfully opened!".format(filename))

#==================================================================
#
#              3) Close Database
#
#==================================================================
def closeDatabase(database):
	if database.is_open:
		database.close()
		print('File successfully closed')
	else:
		print ('No database is currently open')


#==================================================================
#
#              4) Display Record
#
#==================================================================
def displayRecord(database):
	#Check if database is open
	#-------------------------
	if not database.is_open:
		print('No database is currently open')
		return None

	#Gets the primary key from the user
	#----------------------------------
	key = input("Enter the primary key you wish to search for (or \"q\" to quit): ")
	if (key == 'q'):
		return None
	record, position = binarySearch(database, key)
	while( record == -1 and key != 'q') or (key == ''):
		if (key != ''):
			key = input("key {} was not found. Enter a new key (or \"q\" to quit): ".format(key))
		else:
			key = input("Enter the primary key you wish to search for (or \"q\" to quit): ")
		if (key == 'q'):
			return None
		record, position = binarySearch(database, key)

	#Alerts the record was found, splits it by field, and displays the results
	#-------------------------------------------------------------------------
	print('\nRecord {} was found!'.format(record[0]))
	database.config.seek(0)
	next(database.config)
	next(database.config)
	field_names = []
	field_sizes = []
	num_fields = int(database.config.readline())
	for i in range(num_fields):
		name, size = readFieldData((str(database.config.readline())))
		field_names.append(name)
		field_sizes.append(size)
		print('{}: {}'.format(field_names[i], record[i]))

#==================================================================
#
#              5) Update Record
#
#==================================================================
def updateRecord(database):
	#Check if database is open
	#-------------------------
	if not database.is_open:
		print('No database is currently open')
		return None

	key = input("Enter the primary key of the record you would like to change (or \"q\" to quit): ")
	if (key == 'q'):
		return None
	record, position = binarySearch(database, key)
	while( record == -1 and key != 'q'):
		key = input("\nkey {} was not found. Enter a new key (or \"q\" to quit): ".format(key))
		if (key == 'q'):
			return None
		record, position = binarySearch(database, key)

	#Displays the contents of the record
	#-----------------------------------
	print('\nRecord {} was found!'.format(record[0]))
	num_records, record_size, num_fields, field_names, field_sizes, divider = readConfigFile(database)
	for i in range(num_fields):
		print('{}: {}'.format(field_names[i], record[i]))

	#Gets what field will be changed
	#-------------------------------
	field_change = input('\nPlease enter the name of the field you would like to update: ')
	while (field_change not in field_names or field_change == field_names[0] or field_change == ''):
		if (field_change == field_names[0]):
			field_change = input('You cannot change the {}. Please enter a different field: '.format(field_names[0]))
		elif (field_change == ''):
			field_change = input('Please enter the name of the field you would like to update: ')
		else:
			field_change = input('{} is not a field. Please enter a correct field: '.format(field_change))
	idx = field_names.index(field_change)

	#Gets the new value to change the field to
	#-----------------------------------------
	new_value = input('\nWhat would you like to change the {} to: '.format(field_change))
	while (len(new_value) > field_sizes[idx] or new_value == ''):
		if (new_value == ''):
			new_value = input('What would you like to change the {} to: '.format(field_change))
		else:
			new_value = input('The value is too large. Please enter a different one: ')

	#Updates field in database
	#-------------------------
	if (len(new_value) <= field_sizes[idx]):
		database.data.seek(0)
		database.data.seek(record_size * position + sum(field_sizes[0:idx]) + idx)
		for i in range(field_sizes[idx] - len(new_value)):
			new_value+=divider
		database.data.write(new_value)
	else:
		pass

#==================================================================
#
#              6) Create Report
#
#==================================================================
def createReport(database):
	#Check if database is open
	#-------------------------
	if not database.is_open:
		print('No database is currently open')
		return None

	#Reads the data from the config file
	#-----------------------------------
	num_records, record_size, num_fields, field_names, field_sizes, divider = readConfigFile(database)

	#Writes the header data into the report
	#--------------------------------------
	report = open(database.name+'.txt', 'w')
	for i in range(num_fields):
		report.write(field_names[i])
		if (len(field_names[i]) < field_sizes[i]):
			spaces = abs(len(field_names[i]) - field_sizes[i]) + 1
		else:
			spaces = 1
		report.write(' ' * spaces)
	report.write('\n')

	#Writes the first 10 records into the report
	#-------------------------------------------
	num_records_report = 10
	idx = 0
	for i in range(num_records_report):
		record = getRecord(database, idx)
		while (record == []):
			idx += 1
			record = getRecord(database, idx)
		for j, entry in enumerate(record):
			report.write(entry)
			if (len(field_names[j]) > field_sizes[j]):
				spaces = abs(len(entry) - len(field_names[j])) + 1
			else:
				spaces = abs(len(entry) - field_sizes[j]) + 1
			report.write(' ' * spaces)
		report.write('\n')
		idx += 1
	report.close()

	#Displays the results
	#--------------------
	report = open(database.name+'.txt', 'r')
	print('Report is created...\n')
	print('Displaying Results...')
	print('=====================')
	for line in report:
		print(line)
	report.close()

#==================================================================
#
#              7) Add Record
#
#==================================================================
def addRecord(database):
	#Check if database is open
	#-------------------------
	if not database.is_open:
		print('No database is currently open')
		return None

	#Reads the data from the config file
	#-----------------------------------
	num_records, record_size, num_fields, field_names, field_sizes, divider = readConfigFile(database)

	new_record = []
	for i in range(num_fields):
		new_entry = input('\nPlease enter the {} for your new record: '.format(field_names[i]))
		if (i == 0):
			record, location_position = binarySearch(database, new_entry)
			while (not new_entry.isnumeric()) or (new_entry == '') or (record != -1):
				if (record != -1):
					new_entry = input('ID {} already exists. Please enter a new one: '.format(new_entry))
				else:
					new_entry = input('The ID must be an integer. Please enter something different: ')
				record, location_position = binarySearch(database, new_entry)
		while (new_entry == '') or (len(new_entry) > field_sizes[i]):
			if (new_entry == ''):
				new_entry = input('Please enter the {} for your new record: '.format(field_names[i]))
			else:
				new_entry = input('{} is too long. Please enter a new {} : '.format(new_entry, field_names[i]))

		new_record.append(new_entry)

	#Checks if there is room for an insertion
	#----------------------------------------
	#print(location_position)
	#if (getRecord(database, location_position)[0] == divider):
	if (getRecord(database, location_position) == []):
		print('here')
		writeRecord(database, location_position, new_record)
	else:
		#Database is duplicated to add more space and record is added
		#------------------------------------------
		new_file = open('new_file.data', 'w')
		database.data.seek(0,0)
		record_count = 0
		for line in database.data:
			if (line[0] != divider):
				record_count += 1
				new_file.write(line)
				new_file.write(divider*(sum(field_sizes) + num_fields - 1))
				new_file.write('\n')
		new_file.close()
		database.close()
		os.remove(database.name+'.data')
		os.rename('new_file.data', database.name+'.data')
		database.open(database.name)
		record, location_position = binarySearch(database, new_record[0])
		print(new_record[0], location_position)
		writeRecord(database, location_position, new_record)
		record_count += 1
		database.config.seek(0)
		database.config.write(str(record_count))

#==================================================================
#
#              8) Delete Record
#
#==================================================================
def deleteRecord(database):
	#Check if database is open
	#-------------------------
	if not database.is_open:
		print('No database is currently open')
		return None

	num_records, record_size, num_fields, field_names, field_sizes, divider = readConfigFile(database)

	#Gets the primary key from the user
	#----------------------------------
	key = input("Enter the primary key you wish to search for (or \"q\" to quit): ")
	if (key == 'q'):
		return None
	record, position = binarySearch(database, key)
	while( record == -1 and key != 'q') or (key == ''):
		if (key != ''):
			key = input("key {} was not found. Enter a new key (or \"q\" to quit): ".format(key))
		else:
			key = input("Enter the primary key you wish to search for (or \"q\" to quit): ")
		if (key == 'q'):
			return None
		record, position = binarySearch(database, key)

	answer = input('\nAre you sure you wish to delete record {}? (y/n): '.format(key))
	while (answer != 'y' and answer != 'n'):
		answer = input('Are you sure you wish to delete record {}? (y/n): '.format(key))

	if (answer == 'y'):
		record, postion = binarySearch(database, key)
		record = []
		for i in range(num_fields):
			record.append(divider)
		writeRecord(database, position, record)
		database.config.seek(0)
		database.config.write(str(num_records - 1))


#==================================================================
#
#              9) Quit
#
#==================================================================
def deleteDatabase(database):
	if database.is_open:
		database.close()
		print('Database successfully closed...\n')
	# for file in os.listdir():
	# 	if file.endswith(".data") or file.endswith(".config"):
	# 		os.remove(file)

#==================================================================
#
#            Useful Functions
#
#==================================================================

#Funtion that splits the fields in csv file and returns a list of fields
#-----------------------------------------------------------------------
def parseRecord(record):
	records = []
	field = ''
	in_quote = False
	for char in record:

		if (in_quote):
			if (char == '\"'):
				if (field != ''):
					records.append(field)
				field = ''
				in_quote = False
			else:
				field += char
		elif (char == '\"') and (not in_quote):
			in_quote = True
			if (field != ''):
				records.append(field)
			field = ''
		elif (char == ','):
			if (field != ''):
				records.append(field)
			field = ''
		elif (char == '\n'):
			if (field != ''):
				records.append(field)
		elif (char == record[-1] and char != '\n'):
			if (field != ''):
				field += char
				records.append(field)
		else:
			field += char

	return records

#Function that splits the records in the database
#------------------------------------------------
def splitRecord(record):
	split_record = []
	field = ''
	for char in record:
		if (char == '\n'):
			if (field != ''):
				split_record.append(field)
			field = ''
		if (char != '!'):
			field+=char
		elif (char == '!'):
			if (field != ''):
				split_record.append(field)
			field = ''
	return split_record

	#return record

#Searches for ID in database using binary search
#-----------------------------------------------
def binarySearch(database, key):

	#Check if database is open
	#-------------------------
	if not database.is_open:
		return -1, None

	if (key.isnumeric()):
		key = int(key)
	else:
		return -1, None

	#useful variables
	#----------------
	database.config.seek(0)
	num_records = int(database.config.readline())
	record_size = int(database.config.readline())
	low = 0
	#high = (num_records * 2) - 2
	high = 0
	database.data.seek(0)
	for i, line in enumerate(database.data):
		high=i
	high -=1
	found = False
	middle = 0
	results = -1

	#Searches for key
	#----------------
	while (low <= high):

		middle = (low + high) // 2
		record = getRecord(database, middle)
		#while (record[0] == '!'):
		while (record == []):
			middle += 1
			record = getRecord(database, middle)
			if middle > 400:
				break

		#middleid = int(splitRecord(record)[0])
		middleid = int(record[0])
		if (middleid == key):
			return record, middle
		if (low == high):
			return -1, low
		if (middle > high):
			return -1, high
		if (middle < low):
			return -1, low
		if (middleid < key):
			low = middle + 1
		if (middleid > key):
			high = middle - 1
	return -1, middle

# Get record number n (Records numbered from 0 to NUM_RECORDS-1) 
#---------------------------------------------------------------
def getRecord(database, record_num):

	record = ""
	database.config.seek(0)
	num_records = int(database.config.readline()) * 2 - 1	#763
	record_size = int(database.config.readline()) + 1		#152
	f = database.data
	f.seek(0)

	if record_num >= 0 and record_num < num_records:
		for i, line in enumerate(f):
			if (i == record_num):
				record = str(line)
				#print(record)
				break
		# f.seek(0,0)
		# f.seek(record_size * record_num) #offset from the beginning of the file
		# record = f.readline()
		# Success = True
	return splitRecord(record)

def writeRecord(database, position, record):
	num_records, record_size, num_fields, field_names, field_sizes, divider = readConfigFile(database)
	database.config.seek(0)
	num_records = int(database.config.readline()) * 2 - 1	#763
	record_size = int(database.config.readline()) + 1		#152
	f = database.data

	f.seek(0)
	f.seek(record_size * position)
	for idx, entry in enumerate(record):
		f.write(entry)
		f.write(divider*(field_sizes[idx] - len(entry)))
		if (idx < (num_fields - 1)):
			f.write(divider)

#Reads the field data in the config file
#---------------------------------------
def readFieldData(record):
	name = ''
	size = ''
	field_name = ''
	field_size = ''
	for char in record:
		if (char == ' '):
			field_name = name
		elif (char == '\n'):
			field_size = size
		elif (char != ' ') and (not char.isnumeric()):
			name+=char
		elif (char != ' ') and (char.isnumeric()):
			size+=char
	return field_name, int(field_size)

#Reads and returns the metadata from the config file
#---------------------------------------------------
def readConfigFile(database):
	database.config.seek(0)
	num_records = int(database.config.readline())
	record_size = int(database.config.readline()) + 1
	field_names = []
	field_sizes = []
	num_fields = int(database.config.readline())
	for i in range(num_fields):
		name, size = readFieldData((str(database.config.readline())))
		field_names.append(name)
		field_sizes.append(size)
	divider = str(database.config.readline())
	return num_records, record_size, num_fields, field_names, field_sizes, divider

main()	#Calls main program	