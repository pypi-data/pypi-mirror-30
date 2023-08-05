#!/usr/bin/env python3
import demjson

class Tsu4LapeError(Exception): #The default Error class for Tsu4Lape, extend all your code errors from it
	def __init__(self, message, code):
		self.message = valid_message(message)
		self.code = valid_code(code)


	def valid_message(message): #Simple method to garantee that the message will be a string
		if type(message) != type(""):
			raise Exception("The error message must be a String.")
		else:
			return message


	def valid_code(code): #Simple method to garantee that the code will be a int
		if code == 0:
			raise Exception("Cannot be Zero!")
		if type(code) != type(0):
			raise Exception("The error code must be a int.")
		else:
			return code

def reporter(success, test_name, expected_results, results):# A function to make the reports, don't use it
	report = ""
	if success:
		report += test_name + " PASSED!\n"
		report += "=======================\n"
		return report
	else:
		report += test_name + " FAILLED!\n"
		report += "Expected: " + str(expected_results) + "\n"
		report += "Given: " + str(results) + "\n"
		report += "=======================\n"
		return report

def good_test(test_name, function_to_test, args, expected_results): #Don't use it it's just a function to use inside the final test function
	results = function_to_test(args)
	success = results == expected_results
	return reporter(success, test_name, expected_results, results)

def bad_test(test_name, function_to_test, args, expected_results):#Don't use it it's just a function to use inside the final test function
	current_error_code = 0
	current_error_message = ""
	success = False

	try:
		function_to_test(args)
	except Tsu4LapeError as current_error:
		current_error_code = current_error.code
		current_error_message = current_error.message
	else:
		pass

	success = current_error_code == expected_results
	results = str(current_error_code) + ": " + current_error_message
	return reporter(success, test_name, expected_results, results)

def tests_iterator(tests_dict, function_to_test, test_type): #A function to work on all the static tests, don't use it
	report = ""
	for test_name in tests_dict:
		args = tests_dict[test_name][0]
		expected_results = tests_dict[test_name][1]
		report += test_type(test_name, function_to_test, args, expected_results)
	return report

def colateral_tests_iterator(tests_dict, function_to_test, getter_method): #A function to work on all the colateral tests, don't use it
	report = ""
	for test_name in tests_dict:
		args = tests_dict[test_name][0]
		expected_results = tests_dict[test_name][1]
		report += colateral_test(test_name, function_to_test, args, expected_results, getter_method)
	return report

def colateral_test(test_name, method_to_test, args, expected_results, getter_method): # A function to test methods with colateral effects inside objects, Don't use it
	method_to_test(args)
	success = expected_results == getter_method()
	return reporter(success, test_name, expected_results, getter_method())

def function_tester(json_file, function_to_test): #Test a your function with a json file and returns the report as a variable, use it if you like it
	test_dict = demjson.decode(json_file.read())
	goodTests = test_dict["goodTests"]
	badTests = test_dict["badTests"]
	report = ""

	report += tests_iterator(goodTests, function_to_test, good_test)
	report += tests_iterator(badTests, function_to_test, bad_test)

	return report

def method_tester(json_file, function_to_test, getter_method):#Test a your method with a json file and returns the report as a variable, use it if you like it
	test_dict = demjson.decode(json_file.read())
	goodTests = test_dict["goodTests"]
	badTests = test_dict["badTests"]
	report = ""

	report += tests_iterator(goodTests, function_to_test, getter_method)
	report += tests_iterator(badTests, function_to_test, bad_test)

	return report
