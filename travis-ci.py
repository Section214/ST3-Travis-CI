import sublime
import sublime_plugin
import subprocess
import os
import sys
import json
import webbrowser
import urllib.request, urllib.error, urllib.parse

class EventListener(sublime_plugin.EventListener):
	def __init__(self):
		global settings
		settings = sublime.load_settings('Travis-CI.sublime-settings')

	def on_new_async(self, view):
		self.update_status_bar(view)

	def on_clone_async(self, view):
		self.update_status_bar(view)

	def on_load_async(self, view):
		self.update_status_bar(view)

	def on_pre_close(self, view):
		self.update_status_bar(view)

	def on_post_save_async(self, view):
		self.update_status_bar(view)

	def on_activated_async(self, view):
		self.update_status_bar(view)

	def update_status_bar(self, view):
		if view.is_scratch() or view.settings().get('is_widget'):
			return

		travis = TravisStatus(sublime.active_window())
		status = travis.run()

		if status is not None:
			view.set_status("(.0.travis-ci", status)
		else:
			view.erase_status("(.0.travis-ci")


class TravisStatus(sublime_plugin.WindowCommand):

	def run(self):
		return self.check()

	def check(self):
		remote = settings.get('default_remote', 'origin')
		status = None

		self.repos = settings.get('repos', None)

		local_repo = self.get_repo(remote)

		if local_repo is not None:
			if isinstance(self.repos, dict) and local_repo in self.repos:
				if isinstance(self.repos[local_repo], dict) and 'remote' in self.repos[local_repo]:
					repo = self.get_repo(self.repos[local_repo]['remote'])
			else:
				repo = local_repo

			status = self.get_travis_status(repo)

		if status is not None:
			if status == 0:
				status = settings.get('status_prefix', 'Travis: ') + settings.get('status_passing', 'Passing')
			else:
				status = settings.get('status_prefix', 'Travis: ') + settings.get('status_failing', 'Failing')

		return status

	def get_repo(self, remote):
		file_name = self.window.active_view().file_name()
		repo = None

		if file_name is not None:
			file_path, file_name = os.path.split(file_name)
			os.chdir(file_path)

			try:
				matches = subprocess.check_output(['git', 'remote', 'show', remote]).strip()
				matches = matches.decode('utf8', 'ignore').split("\n")

				fetch = list(filter(lambda element: 'Fetch URL' in element, matches))

				if len(fetch) > 0:
					fetch = fetch[0].split(':')

					if len(fetch) > 1:
						fetch = fetch[-1]

				if isinstance(fetch, str) and fetch.find('.git', 0, len(fetch)) != -1:
					repo = fetch.strip('.git')
			except:
				if settings.get('debug_enable', False):
					print('[Travis-CI Git Error] ' + file_path + ' is not a git repository')
		else:
			if settings.get('debug_enable', False):
				print('[Travis-CI File Error] Unsaved file can not be in git repository')

		return repo

	def get_travis_status(self, repo):
		status = None

		try:
			request = urllib.request.urlopen('https://api.travis-ci.org/repos/' + repo + '.json')

			with request as travis_json:
				travis_json = json.loads(travis_json.readall().decode('utf-8'))
				status = travis_json["last_build_status"]
		except urllib.error.HTTPError as error:
			if settings.get('debug_enable', False):
				print('[Travis-CI API Error] ' + str(error.code) + ': ' + error.reason)
		except urllib.error.URLError as error:
			if settings.get('debug_enable', False):
				print('[Travis-CI API Error] ' + str(error.code) + ': ' + error.reason)
		except Exception as error:
			if settings.get('debug_enable', False):
				print('[Travis-CI API Error] ' + error.read().decode())

		return status


##
# Handler for the Travis CI: Show Build command.
# Major props to Adam Presley since a good chunk of
# this class was forked from his View In Browser plugin.
# (https://github.com/adampresley/sublime-view-in-browser)
##
class TravisShowBuild(sublime_plugin.WindowCommand):

	##
	# Do all the things
	##
	def run(self):
		travis = TravisStatus(sublime.active_window())
		remote = settings.get('default_remote', 'origin')
		self.repos = settings.get('repos', None)
		local_repo = travis.get_repo(remote)
		os_name = self.get_os_name()
		platform = self.get_platform()
		selected_os = settings.get(os_name)
		browser = settings.get('browser', 'firefox')

		# Get the repo path to open
		if local_repo is not None:
			if isinstance(self.repos, dict) and local_repo in self.repos:
				if isinstance(self.repos[local_repo], dict) and 'remote' in self.repos[local_repo]:
					repo = self.get_repo(self.repos[local_repo]['remote'])
			else:
				repo = local_repo

		# Setup the base command
		try:
			base_command = self.get_base_command(selected_os[platform][browser], os_name)
		except:
			base_command = None

		# Setup the URL
		travis_url = 'https://travis-ci.org/' + repo

		# Go!
		if base_command is not None:
			command = "%s %s" % (base_command, travis_url,)
			self.open_browser(command, os_name)
		else:
			command = webbrowser.open_new_tab(travis_url)

	##
	# Returns the correct base command
	# for a given operating system
	##
	def get_base_command(self, command, os_name):
		base_command = command

		if os_name == 'nt':
			base_command = self.expand_windows_user_shell_folder(base_command)

		return base_command

	##
	# Get the current OS
	# i.e. darwin, nt, linux
	##
	def get_os_name(self):
		return os.name

	##
	# Get the current platform
	# i.e. posix, win32
	##
	def get_platform(self):
		return sys.platform

	##
	# Grab all Windows shell folder locations from the registry
	##
	def get_windows_user_shell_folders(self):
		import winreg as _winreg

		return_dict = {}

		# Open the registry hive
		try:
			hive = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
		except WindowsError:
			if settings.get('debug_enable', False):
				print('[Travis-CI Registry Error] Can not connect to registry hive HKEY_CURRENT_USER')
			return return_dict

		# Open the registry key where Windows stores shell folders
		try:
			key = _winreg.OpenKey(Hive, 'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
		except WindowsError:
			if settings.get('debug_enable', False):
				print('[Travis-CI Registry Error] Can not open registry key')
			_winreg.CloseKey(hive)
			return return_dict

		# Enumerate all the things and return in a dictionary
		try:
			for i in range(0, _winreg.QueryInfoKey(key)[1]):
				name, value, val_type = _winreg.EnumValue(key, i)
				return_dict[name] = value.encode('ascii')
				i += 1
			_winreg.CloseKey(key)
			_winreg.CloseKey(hive)
			return return_dict
		except WindowsError:
			if settings.get('debug_enable', False):
				print('[Travis-CI Registry Error] An unknown error occurred')
			_winreg.CloseKey(key)
			_winreg.CloseKey(hive)
			return {}

	##
	# Get the path of a Windows variable
	##
	def expand_windows_user_shell_folder(self, command):
		browser_command = ''
		windows_folders = self.get_windows_user_shell_folders()
		special_folder = re.sub(r"%([A-Za-z\s]+)%.*", "\\1", command)

		if special_folder != command:
			expand_folder = windows_folders[special_folder].replace('\\', '\\\\')
			browser_command = re.sub(r"%[A-Za-z\s]+%(.*)", "%s\\1" % expanded_folder, command)
		else:
			browser_command = command

		return browser_command

	##
	# Open the specified browser
	##
	def open_browser(self, command, os_name):
		use_shell = False if os_name != 'posix' else True
		subprocess.Popen(command, shell=use_shell)