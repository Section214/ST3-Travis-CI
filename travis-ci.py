import sublime
import sublime_plugin
import subprocess
import os
import re
import urllib.request
import json

class GitManager:
	def __init__(self, view):
		settings = sublime.load_settings('Travis-CI.sublime-settings')
		self.view = view
		self.git = settings.get("git", "git")
		self.remote = settings.get("remote", "origin")
		self.prefix = settings.get("prefix", "Travis: ")

	def run_git(self, cwd=None):
		settings = sublime.load_settings('Travis-CI.sublime-settings')
		plat = sublime.platform()
		ret = None
		if not cwd:
			cwd = self.getcwd()
		if cwd:
			cmd = [self.git] + ["remote"] + ["show"] + [self.remote]
			if plat == "windows":
				startupinfo = subprocess.STARTUPINFO()
				startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, startupinfo=startupinfo)
			else:
				my_env = os.environ.copy()
				my_env["PATH"] = "/usr/local/bin/:" + my_env["PATH"]
				p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=my_env)
			p.wait()
			stdoutdata, _ = p.communicate()
			ret = stdoutdata.decode('utf-8')
			return ret

	def get_remote(self, remote):
		ret = None
		if remote is not None:
			output = re.search("(Fetch URL)(.*)(?=.git)", remote, flags=re.MULTILINE)
			if output is not None:
				if output.group(0):
					output = output.group(0).split(":")
			if output is not None:
				if output[2]:
					ret = output[2]
		return ret

	def get_travis_json(self, remote):
		ret = None
		if remote is not None:
			req = urllib.request.Request("https://api.travis-ci.org/repos/" + remote + ".json")
			with urllib.request.urlopen(req) as response:
				travis_json = json.loads(response.readall().decode('utf-8'))
				ret = travis_json["last_build_status"]
		return ret

	def getcwd(self):
		f = self.view.file_name()
		cwd = None
		if f:
			cwd = os.path.dirname(f)
		if not cwd:
			window = self.view.window()
			if window:
				pd = window.project_data()
				if pd:
					cwd = pd.get("folders")[0].get("path")
		return cwd

	def status(self):
		ret = None
		remote = self.run_git()
		remote = self.get_remote(remote)
		status = self.get_travis_json(remote)
		if status is not None:
			if status == 0:
				ret = 'Passing'
			else:
				ret = 'Failing'
			settings = sublime.load_settings('Travis-CI.sublime-settings')
			ret = self.prefix + ret
		return ret

class TravisStatusBarHandler(sublime_plugin.EventListener):
	def update_status_bar(self, view):
		sublime.set_timeout_async(lambda: self._update_status_bar(view), 1000)

	def _update_status_bar(self, view):
		if view.is_scratch() or view.settings().get('is_widget'):
			return
		gm = GitManager(view)
		status = gm.status()
		if status is not None:
			view.set_status("(.0.travis-ci", status)
		else:
			view.erase_status("travis-ci")

	def on_new(self, view):
		self.update_status_bar(view)

	def on_load(self, view):
		self.update_status_bar(view)

	def on_activated(self, view):
		self.update_status_bar(view)

	def on_post_save(self, view):
		self.update_status_bar(view)

	def on_pre_close(self, view):
		self.update_status_bar(view)

	def on_window_command(self, window, command_name, args):
		if command_name == "hide_panel":
			self.update_status_bar(window.active_view())