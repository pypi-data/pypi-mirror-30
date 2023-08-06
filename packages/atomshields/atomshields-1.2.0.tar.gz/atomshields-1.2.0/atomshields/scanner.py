# -*- coding:utf8 -*-

import os
import shutil
import glob
import ast
import sys
import collections
from datetime import datetime
from ConfigParser import ConfigParser
from termcolor import colored
from models import Issue

class AtomShieldsScanner(object):
	"""
	Class in charge of orchestrating the execution of the cherckers and the results.
	"""


	# Static block.
	# Check if paths are writable and change it else

	HOME = "/usr/local/share/atomshields"
	HOME_2 = os.path.expanduser("~/.atomshields")

	if not os.access(HOME, os.W_OK):
		CHECKERS_DIR = os.path.join(HOME_2, "checkers")
		REPORTS_DIR = os.path.join(HOME_2, "reports")
	else:
		CHECKERS_DIR = os.path.join(HOME, "checkers")
		REPORTS_DIR = os.path.join(HOME, "reports")

	CONFIG_PATH = os.path.expanduser("~/.atomshields/config")

	def __init__(self, path, verbose = False):
		self._path = path
		self._project = None
		self._issues = []
		self._config_file = AtomShieldsScanner.CONFIG_PATH
		self.verbose = verbose

	@staticmethod
	def _debug(message, color=None, attrs=None):
		"""
		Print a message if the class attribute 'verbose' is enabled

		Args:
			message (str): Message to print
		"""
		if attrs is None:
			attrs = []
		if color is not None:
			print colored(message, color, attrs=attrs)
		else:
			if len(attrs) > 0:
				print colored(message, "white", attrs=attrs)
			else:
				print message

	def debug(self, message, color=None, attrs=None):
		if self.verbose:
			if attrs is None:
				attrs = []
			AtomShieldsScanner._debug(message, color=color, attrs=attrs)

	@property
	def path(self):
		"""
		Getter for 'path' property

		Returns:
			string: Absolute path to target directory
		"""
		return self._path

	@path.setter
	def path(self, value):
		"""
		Setter for 'path' property

		Args:
			value (str): Path to target directory

		"""
		self._path = os.path.abspath(value)


	@property
	def project(self):
		"""
		Getter for 'project' property

		Returns:
			string: Projects's name
		"""
		return self._project

	@project.setter
	def project(self, value):
		"""
		Setter for 'project' property

		Args:
			value (str): Project's name

		"""
		self._project = value


	@property
	def configFile(self):
		"""
		Getter for 'configFile' property

		Returns:
			str: Path to config file
		"""
		return self._config_file

	@configFile.setter
	def configFile(self, value):
		"""
		Setter for 'configFile' property

		Args:
			value (str): Path to config file

		"""
		self._config_file = os.path.abspath(value)

	@property
	def config(self):
		"""
		Getter for 'config' property

		Returns:
			str: Path to config file
		"""
		return self._config

	@config.setter
	def config(self, value):
		"""
		Setter for 'config' property

		Args:
			value (dict): Dictionary which contains the config

		"""
		self._config = value

	@property
	def issues(self):
		"""
		Getter for 'issues' property

		Returns:
			list: List of Issue instances
		"""
		return self._issues

	@issues.setter
	def issues(self, value):
		"""
		Setter for 'issues' property

		Args:
			value (list): List of Issue instances

		"""
		self._issues = value


	@staticmethod
	def setup():
		"""
			Creates required directories and copy checkers and reports.
		"""


		# # Check if dir is writable
		# if not os.access(AtomShieldsScanner.HOME, os.W_OK):
		# 	AtomShieldsScanner.HOME = os.path.expanduser("~/.atomshields")
		# 	AtomShieldsScanner.CHECKERS_DIR = os.path.join(AtomShieldsScanner.HOME, "checkers")
		# 	AtomShieldsScanner.REPORTS_DIR = os.path.join(AtomShieldsScanner.HOME, "reports")


		if not os.path.isdir(AtomShieldsScanner.CHECKERS_DIR):
			os.makedirs(AtomShieldsScanner.CHECKERS_DIR)
		if not os.path.isdir(AtomShieldsScanner.REPORTS_DIR):
			os.makedirs(AtomShieldsScanner.REPORTS_DIR)


		# Copy all checkers
		for f in AtomShieldsScanner._getFiles(os.path.join(os.path.dirname(os.path.realpath(__file__)), "checkers"), "*.py"):
			AtomShieldsScanner.installChecker(f)
		# Copy all reports
		for f in AtomShieldsScanner._getFiles(os.path.join(os.path.dirname(os.path.realpath(__file__)), "reports"), "*.py"):
			AtomShieldsScanner.installReport(f)

		AtomShieldsScanner._executeMassiveMethod(path=AtomShieldsScanner.CHECKERS_DIR, method="install", args={})


		config_dir = os.path.dirname(AtomShieldsScanner.CONFIG_PATH)
		if not os.path.isdir(config_dir):
			os.makedirs(config_dir)


	@staticmethod
	def writeConfig(config, configFile = None):
		if configFile is None:
			configFile = AtomShieldsScanner.CONFIG_PATH
		with open(configFile, 'wb') as configfile:

			# Sort sections
			data = collections.OrderedDict()
			for k in sorted(config._sections.keys()):
				data[k] = config._sections[k]

			config._sections = data
			config.write(configfile)



	@staticmethod
	def installPlugin(origin, destination):
		if os.path.isfile(origin) and os.path.isdir(destination):
			shutil.copy(origin, destination)

	@staticmethod
	def installChecker(path, exclude = ["__init__.py", "base.py"]):
		AtomShieldsScanner.installPlugin(path, AtomShieldsScanner.CHECKERS_DIR)
		checker_basename = os.path.basename(path)
		checker_path = os.path.join(AtomShieldsScanner.CHECKERS_DIR, checker_basename)
		if checker_basename not in exclude:
			instance = AtomShieldsScanner._getClassInstance(checker_path)
			config = AtomShieldsScanner._loadConfig(AtomShieldsScanner.CONFIG_PATH)
			AtomShieldsScanner._addConfig(instance = instance, config = config, parent_section = 'checkers')
			AtomShieldsScanner.writeConfig(config, AtomShieldsScanner.CONFIG_PATH)


	@staticmethod
	def installReport(path, exclude = ["__init__.py", "base.py"]):
		AtomShieldsScanner.installPlugin(path, AtomShieldsScanner.REPORTS_DIR)
		report_basename = os.path.basename(path)
		report_path = os.path.join(AtomShieldsScanner.REPORTS_DIR, report_basename)
		if report_basename not in exclude:
			instance = AtomShieldsScanner._getClassInstance(report_path)
			config = AtomShieldsScanner._loadConfig(AtomShieldsScanner.CONFIG_PATH)
			AtomShieldsScanner._addConfig(instance = instance, config = config, parent_section = 'reports')
			AtomShieldsScanner.writeConfig(config, AtomShieldsScanner.CONFIG_PATH)


	@staticmethod
	def uninstallPlugin(path, name = None, classArgs = None):
		if classArgs is None:
			classArgs = {}

		if os.path.isfile(path) and path.endswith(".py"):
			os.remove(path)
		else:
			if os.path.isdir(path) and name is not None:
				exclude = ["__init__.py", "base.py"]
				for f in AtomShieldsScanner._getFiles(path, "*.py", exclude=exclude):
					try:
						instance = AtomShieldsScanner._getClassInstance(path = f, args = classArgs)
						if instance.__class__.NAME.lower() == name.lower():
							# This plugin
							os.remove(f)
					except Exception as e:
						print "[!] {e}".format(e=e)
						continue


	@staticmethod
	def uninstallChecker(name):
		AtomShieldsScanner.uninstallPlugin(path = AtomShieldsScanner.CHECKERS_DIR, name = name, classArgs = {})
		section = 'checkers/{n}'.format(n=name)
		config = AtomShieldsScanner._loadConfig(AtomShieldsScanner.CONFIG_PATH)
		config.remove_section(section)
		with open(AtomShieldsScanner.CONFIG_PATH, 'wb') as configfile:
			config.write(configfile)

	@staticmethod
	def uninstallReport(name):
		AtomShieldsScanner.uninstallPlugin(path = AtomShieldsScanner.REPORTS_DIR, name = name,  classArgs = {})
		section = 'reports/{n}'.format(n=name)
		config = AtomShieldsScanner._loadConfig(AtomShieldsScanner.CONFIG_PATH)
		config.remove_section(section)
		with open(AtomShieldsScanner.CONFIG_PATH, 'wb') as configfile:
			config.write(configfile)

	@staticmethod
	def _addConfig(instance, config, parent_section):
		"""
		Writes a section for a plugin.

		Args:
			instance (object): Class instance for plugin
			config (object): Object (ConfigParser) which the current config
			parent_section (str): Parent section for plugin. Usually 'checkers' or 'reports'
		"""
		try:
			section_name = "{p}/{n}".format(p = parent_section, n=instance.NAME.lower())
			config.add_section(section_name)
			for k in instance.CONFIG.keys():
				config.set(section_name, k, instance.CONFIG[k])
		except Exception as e:
			print "[!] %s" % e

	@staticmethod
	def generateConfig(show = False):

		config = ConfigParser()

		# Add Default config
		config.add_section("atomshields")
		config.set("atomshields", "enabled", True)



		# def __addConfig(instance, config, parent_section):
		# 	try:
		# 		section_name = "{p}/{n}".format(p = parent_section, n=instance.NAME)
		# 		config.add_section(section_name)
		# 		for k in instance.CONFIG.keys():
		# 			config.set(section_name, k, instance.CONFIG[k])
		# 	except Exception as e:
		# 		print "[!] %s" % e


		config.add_section("checkers")
		config.set("checkers", "enabled", True)
		AtomShieldsScanner._executeMassiveMethod(path=AtomShieldsScanner.CHECKERS_DIR, method=AtomShieldsScanner._addConfig, args={"config": config, "parent_section": "checkers"})

		config.add_section("reports")
		config.set("reports", "enabled", True)
		AtomShieldsScanner._executeMassiveMethod(path=AtomShieldsScanner.REPORTS_DIR, method=AtomShieldsScanner._addConfig, args={"config": config, "parent_section": "reports"})

		with open(AtomShieldsScanner.CONFIG_PATH, 'wb') as configfile:
			config.write(configfile)

		if show:
			f = open(AtomShieldsScanner.CONFIG_PATH, 'r')
			content = f.read()
			f.close()
			print content

		return config


	def showScanProperties(self):
		self.debug("")
		self.debug('{:<20}  {:<60}'.format("Path: ", self.path))
		self.debug('{:<20}  {:<60}'.format("Project: ", self.project))
		self.debug("")

	def checkProperties(self):
		if not self.path:
			raise AssertionError("Path is required")
		if not self.project:
			raise AssertionError("Project is required")

	def getConfig(self, section = None):
		"""
		Returns a dictionary which contains the current config. If a section is setted,
		only will returns the section config

		Args:
			section (str): (Optional) Section name.

		Returns:
			dict: Representation of current config
		"""
		data = {}
		if section is None:
			for s in self.config.sections():
				if '/' in s:
					# Subsection
					parent, _s = s.split('/')
					data[parent][_s] = dict(self.config.items(s))
				else:
					data[s] = dict(self.config.items(s))
		else:
			# Only one section will be returned
			data = dict(self.config.items(section))
		return data

	@staticmethod
	def _loadConfig(path):
		if path is not None and os.path.isfile(path):
			handler = ConfigParser()
			handler.read(path)
			return handler
		else:
			raise Exception('Path to config file is not setted!')

	def loadConfig(self):
		config = self.__class__._loadConfig(self.configFile)
		self.config = config

	@staticmethod
	def _getClassName(path):
		if not path.endswith(".py"):
			return False

		with open(path) as f:
			node = ast.parse(f.read())
		return [n for n in node.body if isinstance(n, ast.ClassDef)][0].name

	@staticmethod
	def _getFiles(path, extension="*.py", exclude=None):
		if exclude is None:
			exclude = []
		_p = os.path.join(path, extension)
		return [fn for fn in glob.glob(_p) if not os.path.basename(fn) in exclude]

	@staticmethod
	def _getClassInstance(path, args=None):
		"""
		Returns a class instance from a .py file.

		Args:
			path (str): Absolute path to .py file
			args (dict): Arguments passed via class constructor

		Returns:
			object: Class instance or None
		"""
		if not path.endswith(".py"):
			return None

		if args is None:
			args = {}

		classname = AtomShieldsScanner._getClassName(path)
		basename = os.path.basename(path).replace(".py", "")
		sys.path.append(os.path.dirname(path))
		try:
			mod = __import__(basename, globals(), locals(), [classname], -1)
			class_ = getattr(mod, classname)
			instance = class_(**args)
		except Exception as e:
			AtomShieldsScanner._debug("[!] %s" % e)
			return None
		finally:
			sys.path.remove(os.path.dirname(path))
		return instance

	@staticmethod
	def _executeMassiveMethod(path, method, args=None, classArgs = None):
		"""
		Execute an specific method for each class instance located in path

		Args:
			path (str): Absolute path which contains the .py files
			method (str): Method to execute into class instance

		Returns:
			dict: Dictionary which contains the response for every class instance.
				  The dictionary keys are the value of 'NAME' class variable.
		"""
		response = {}

		if args is None:
			args = {}

		if classArgs is None:
			classArgs = {}

		sys.path.append(path)
		exclude = ["__init__.py", "base.py"]
		for f in AtomShieldsScanner._getFiles(path, "*.py", exclude=exclude):
			try:
				instance = AtomShieldsScanner._getClassInstance(path = f, args = classArgs)
				if instance is not None:
					if callable(method):
						args["instance"] = instance
						output = method(**args)
						response[instance.__class__.NAME] = output
					else:
						if hasattr(instance, method):
							output = getattr(instance, method)(**args)
							response[instance.__class__.NAME] = output
						else:
							continue

			except Exception as e:
				AtomShieldsScanner._debug("[!] %s" % e)
		sys.path.remove(path)
		return response


	def executeCheckers(self):


		def __run(instance):
			instance.project = self.project
			instance.path = self.path
			section = 'checkers/{n}'.format(n = instance.__class__.NAME)

			instance.config = self.getConfig(section = section)
			if self.config.has_option(section, 'enabled'):
				enabled = self.config.getboolean(section, 'enabled')
				if enabled:
					return instance.run()
			else:
				return instance.run()

		return AtomShieldsScanner._executeMassiveMethod(path=AtomShieldsScanner.CHECKERS_DIR, method=__run, args={})

	def executeReports(self):

		# Get the current report config
		def _run(instance):
			instance.project = self.project
			section = 'reports/{n}'.format(n = instance.__class__.NAME)
			instance.config = self.getConfig(section = section)

			if self.config.has_option(section, 'enabled'):
				enabled = self.config.getboolean(section, 'enabled')
				if enabled:
					return instance.run()
			else:
				return instance.run()


		return AtomShieldsScanner._executeMassiveMethod(path=AtomShieldsScanner.REPORTS_DIR, method=_run, args={}, classArgs={"issues": self.issues})


	def saveIssue(self, issue):
		if issue is not None:
			if issue.__class__.__name__ == Issue.__name__:
				self.issues.append(issue)

	def isStable(self):
		for issue in self.issues:
			if not issue.potential:
				if issue.severity in [Issue.SEVERITY_LOW, Issue.SEVERITY_MEDIUM, Issue.SEVERITY_HIGH, Issue.SEVERITY_CRITICAL]:
					return False
		return True

	def showSummary(self):
		severities = {Issue.SEVERITY_INFO: 0, Issue.SEVERITY_LOW: 0, Issue.SEVERITY_MEDIUM: 0,
						Issue.SEVERITY_HIGH: 0, Issue.SEVERITY_CRITICAL: 0}
		for issue in self.issues:
			if issue.severity in severities.keys():
				severities[issue.severity] += 1

		print ""
		print ""
		print colored("%-20s\t%-20s" % (Issue.SEVERITY_INFO, severities[Issue.SEVERITY_INFO]), "cyan")
		print colored("%-20s\t%-20s" % (Issue.SEVERITY_LOW, severities[Issue.SEVERITY_LOW]), "green")
		print colored("%-20s\t%-20s" % (Issue.SEVERITY_MEDIUM, severities[Issue.SEVERITY_MEDIUM]), "yellow")
		print colored("%-20s\t%-20s" % (Issue.SEVERITY_HIGH, severities[Issue.SEVERITY_HIGH]), "red")
		print colored("%-20s\t%-20s" % (Issue.SEVERITY_CRITICAL, severities[Issue.SEVERITY_CRITICAL]), "magenta")
		print "-"*30
		print colored("%-20s\t%-20s" % ("Total:", len(self.issues)), "white", attrs=[])
		print ""
		print ""

		if not self.isStable():
			print "This execution has been ", colored("UNSTABLE", "red", attrs=["bold", "blink"])
		else:
			print "This execution has been ", colored("STABLE", "green", attrs=["bold", "blink"])

		print ""



	def run(self):
		"""
		Run a scan in the path setted.
		"""

		self.checkProperties()

		self.debug("[*] Iniciando escaneo de AtomShields con las siguientes propiedades. . . ")

		self.showScanProperties()

		self.loadConfig()

		# Init time counter
		init_ts = datetime.now()

		# Execute plugins
		cwd = os.getcwd()
		os.chdir(self.path)
		issues = self.executeCheckers()
		os.chdir(cwd)




		# Finish time counter
		end_ts = datetime.now()
		duration = '{}'.format(end_ts - init_ts)

		# Process and set issues
		for plugin in issues.keys():
			value = issues[plugin]
			if isinstance(value, list):
				map(self.saveIssue, value)
			else:
				self.saveIssue(value)



		# Execute reports
		print ""
		self.executeReports()


		# Print summary output.
		self.debug("")
		self.debug("Duration: {t}".format(t=duration))
		self.showSummary()

		return self.issues
