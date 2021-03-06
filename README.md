# Travis-CI

Simple Travis CI integration for Sublime Text 3

# Installation

## Package Control

+ Install [Package Control](http://wbond.net/sublime_packages/package_control)
+ Run the "Package Control: Install Package" command from the command palette
+ Search for `Travis-CI` in the package list

##### NOTE: This is the recommended installation method.

## Manual Installation

If you want to contribute to the plugin (or you're just weird and hate Package Control), you can clone the plugin repository by navigating to the "Packages" directory and running the following command:

`git clone git://github.com/Section214/ST3-Travis-CI`

# I Can Haz Settings?

	// Debug logging
	// If enabled, this dumps debugging data to the console
	//"debug_enable": true,

	// By default, we look for git in your environment path.
	// If your git executable isn't in path, you can set an
	// absolute path here (but ask yourself why it isn't in
	// your path in the first place!!!)
	// "git": "/usr/bin/git",

	// Set the name of the default remote to retrieve build
	// status for. If none is specified, the standard 'origin'
	// is used.
	//"default_remote": "origin",

	// Set the prefix for the status line item
	//"status_prefix": "Travis: ",

	// Set the text for the status line item when the build
	// is passing.
	//"status_passing": "Passing",

	// Set the text for the status line item when the build
	// is failing.
	//"status_failing": "Failing",

	// Per-repo settings
	// At the moment, the only per-repo setting is the
	// 'remote' setting. Allows you to override the default
	// remote defined above on a per-repo basis.
	//"repos": {
	//	"Section214/ST3-Travis-CI": {
	//		"remote": "upstream"
	//	}
	//},

	// Browser settings
	// Specify the browser to open Travis-CI in when viewing
	// builds. Specified browser must map to one of the available
	// browsers in the browser mapping section below. You can
	// add custom browsers as you see fit!
	//"browser": "chrome",

	// Browser mapping
	// Feel free to use the format below to add your own custom
	// browsers! Just make sure you add them in the right section...
	"posix": {
		"linux": {
			"firefox": "firefox -new-tab",
			"chrome": "google-chrome",
			"chrome64": "google-chrome",
			"chromium": "chromium"
		},
		"linux2": {
			"firefox": "firefox -new-tab",
			"chrome": "google-chrome",
			"chrome64": "google-chrome",
			"chromium": "chromium"
		},
		"darwin": {
			"firefox": "open -a \"/Applications/Firefox.app\"",
			"safari": "open -a \"/Applications/Safari.app\"",
			"chrome": "open -a \"/Applications/Google Chrome.app\"",
			"chrome64": "open -a \"/Applications/Google Chrome.app\"",
			"yandex": "open -a \"/Applications/Yandex.app\""
		}
	},
	"nt": {
		"win32": {
			"firefox": "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe -new-tab",
			"iexplore": "C:\\Program Files\\Internet Explorer\\iexplore.exe",
			"chrome": "%Local AppData%\\Google\\Chrome\\Application\\chrome.exe",
			"chrome64": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
			"yandex": "%Local AppData%\\Yandex\\YandexBrowser\\browser.exe"
		}
	}

# Issues

If you find a bug let us know [here](https://github.com/Section214/ST3-Travis-CI/issues?state=open)!

# Contributions

Anyone is welcome to help improve this plugin.

There are various ways you can contribute:

1. Open an [issue](https://github.com/Section214/ST3-Travis-CI/issues?state=open) on GitHub
2. Send us a pull request with your own bug fixes and/or new features
3. Provide feedback and suggestions on [enhancements](https://github.com/Section214/ST3-Travis-CI/issues?direction=desc&labels=Enhancement&page=1&sort=created&state=open)