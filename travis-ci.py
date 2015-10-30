import sublime
import sublime_plugin
import subprocess
import os
import json
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

	#def update_status_bar(self, view):
		#sublime.set_timeout_async(lambda: self._update_status_bar(view), 1000)

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

		if settings.get('repos'):
			self.repos = settings.get('repos', {})

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