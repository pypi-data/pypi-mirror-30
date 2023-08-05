#!/usr/bin/env python3

import demjson

class Tsu4lape_Static:

	@staticmethod
	def json_to_dict(json_file):
		to_return = demjson.decode(json_file.read())
		return to_return

	@staticmethod
	def get_good_tests(json_dict):
		return json_dict["goodTests"]

	@staticmethod
	def get_bad_tests(json_dict):
		return json_dict["badTests"]

	def get_good_tests_list(self, tests_dict):
		tests_list = []
		for test_name in tests_dict:
			args = tests_dict[test_name]["args"]
			result = tests_dict[test_name]["result"]

			tests_list.append(Tsu4Lape_Good_Test(test_name, args, result, self.function))

		return tests_list

	def get_bad_tests_list(self, tests_dict):
		tests_list = []
		for test_name in tests_dict:
			args = tests_dict[test_name]["args"]
			result = tests_dict[test_name]["result"]

			tests_list.append(Tsu4Lape_Bad_Test(test_name, args, result, self.function))

		return tests_list

	def get_final_test_list(self, json_file):
		biggest_test_dict = self.json_to_dict(json_file)
		good_tests_dict = self.get_good_tests(biggest_test_dict)
		bad_tests_dict = self.get_bad_tests(biggest_test_dict)
		good_tests_list = self.get_good_tests_list(good_tests_dict)
		bad_tests_list = self.get_bad_tests_list(bad_tests_dict)

		final_test_list = []

		if len(good_tests_list) > 0: final_test_list.extend(good_tests_list)
		if len(bad_tests_list) > 0: final_test_list.extend(bad_tests_list)

		if len(final_test_list) <= 0: raise Exception("Empty test list.")

		return final_test_list

	def __init__(self, json_file, function):
		self.function = function
		self.test_list = self.get_final_test_list(json_file)

	def print_report(self):
		report = ""
		for test in self.test_list:
			report += test.get_report()
		print(report)

class Tsu4Lape_Bad_Test:
	def __init__(self, test_name, args, result, function):
		self.test_name = test_name
		self.args = args
		self.expected_result = result
		self.function = function
		self.result = None
		self.success = self.evaluate()
		self.error_ocurred = False
		self.error = None

	def evaluate(self):
		try:
			self.result == function(*args)
		except Exception as current_error:
			if current_error.message == result:
				return True
			else:
				self.error_ocurred = True
				self.error = current_error
				return False
		else:
			return False

	def get_report(self):
		report = ""
		if self.success:
			report += self.test_name + " PASSED!\n"
			report += "=========================\n"
		else:
			if self.error_ocurred:
				report += self.test_name + " FAILLED!\n"
				report += "The following error ocurred:\n"
				report += self.error.message + "\n"
				report += "=========================\n"
			else:
				report += self.test_name + " FAILLED!\n"
				report += "A error was expected but no error ocurred.\n"
				report += "=========================\n"
		return report

class Tsu4Lape_Good_Test(Tsu4Lape_Bad_Test):
	def __init__(self, test_name, args, expected_result, function):
		super(Tsu4Lape_Good_Test, self).__init__(test_name, args, expected_result, function)

	def evaluate(self):
		try:
			self.result = self.function(*self.args)
			if self.result == self.expected_result:
				return True
			else:
				return False
		except Exception as current_error:
			self.error_ocurred = True
			self.error = current_error
			return False
		else:
			pass

	def get_report(self):
		report = ""
		if self.success:
			report += self.test_name + " PASSED!\n"
			report += "=========================\n"
		else:
			if self.error_ocurred:
				report += self.test_name + " FAILLED!\n"
				report += "The following error ocurred:\n"
				report += self.error.message + "\n"
				report += "=========================\n"
			else:
				report += self.test_name + " FAILLED!\n"
				report += "Expected: " + str(self.expected_result) + "\n"
				report += "Received: " + str(self.result) + "\n"
				report += "=========================\n"
		return report

class Tsu4lape_Colateral(Tsu4lape_Static):

	def __init__(self, json_file, function, getter_method):
		super(Tsu4lape_Colateral, self).__init__(json_file, function)
		self.getter_method = getter_method
