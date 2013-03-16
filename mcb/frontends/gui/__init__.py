from pprint import pprint
import sys

from gi.repository import Gtk, Gdk, GObject

from mcb.frontends import Frontend
from mcb import utils
from mcb import Plugin
from mcb import ProgressHandler
from mcb.runner import ThreadRunner

currentModule = sys.modules[__name__]

class GuiProgressHandler(ProgressHandler):

	def __init__(self):
		ProgressHandler.__init__(self)
		self.mainProgress = None
		self.gui_finished_callback = None

	def onTaskAdded(self, name, progress):
		self.mainProgress.set_fraction
		print("added task: " + name)

	def onTaskActivated(self, name, progress):
		print("Starting task: " + name)

	def onProgressChanged(self, name, progress):
		print("Progress: {p}%".format(p=int(progress*100)))

	def onTaskFinished(self, name, task_progress):
		Gdk.threads_enter()
		self.mainProgress.set_fraction(task_progress)
		self.mainProgress.set_text('{a}/{b}'.format(
			a=len(self.getFinishedTasks()),
			b=len(self.tasks)
		))
		Gdk.threads_leave()

		print("Finished task: " + name)

		if self.gui_finished_callback:
			self.gui_finished_callback()

class Gui(Frontend):

	def __init__(self):
		self.config = self.getConfig('~/.mycloudbackup')

		self.serviceTypes = utils.getAllServices()
		self.services = self.config.getServices()

		self.outputTypes = utils.getAllOutputs()
		self.outputs = self.config.getOutputs()

	def run(self):
		self.mainWindow = win = MainWindow(self)
		win.connect("delete-event", Gtk.main_quit)

		GObject.threads_init()

		win.showScreen('Home')
		Gtk.main()

	def updateConfig(self):
		self.config.importServices(self.services)
		self.config.importOutputs(self.outputs)

		self.config.toFile()

	def getRunner(self):
		handler = GuiProgressHandler()

		runner = ThreadRunner(self.config)
		runner.setProgressHandler(handler)

		return runner

class Window(Gtk.Window):

	def __init__(self, app, title):
		Gtk.Window.__init__(self, title=title)
		self.app = app
		self.mainWidget = None

	def showScreen(self, screen, data=None):
		if type(screen) == str:
			print('Showing screen ' + screen)
			widget = getattr(self, 'screen' + screen)(data)
		else:
			print('Showing screen ' + screen.__name__)
			widget = screen(self.app, data).build()

		if widget:
			if self.mainWidget:
				self.remove(self.mainWidget)

			self.mainWidget = widget
			self.add(widget)
			self.show_all()

class Screen(object):

	def __init__(self, app, data=None):
		self.app = app
		self.data = data

	def build():
		# implement in subclass
		pass

class MainWindow(Window):

	def __init__(self, app):
		Window.__init__(self, app, title='MyCloudBackup')

		self.app = app
		self.set_border_width(30)

	def screenHome(self, data=None):
		mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		controlBox = Gtk.Box(spacing=20)
		mainBox.add(controlBox)

		# Action buttons
		buttonRun = Gtk.Button(label='Run Backups')
		buttonRun.connect('clicked', lambda button: self.showScreen(ScreenRunBackups))
		controlBox.add(buttonRun)

		buttonAdd = Gtk.Button(label='Add Service')
		buttonAdd.connect('clicked', lambda button: self.showScreen('PluginSelect', 'service'))
		controlBox.add(buttonAdd)

		buttonAdd = Gtk.Button(label='Add Output')
		buttonAdd.connect('clicked', lambda button: self.showScreen('PluginSelect', 'output'))
		controlBox.add(buttonAdd)

		store = Gtk.ListStore(str, str)

		# services list
		label = Gtk.Label('Services')
		mainBox.add(label)

		grid = Gtk.Grid()
		grid.set_column_spacing(30)
		grid.set_row_spacing(10)
		mainBox.add(grid)

		index = 0
		for service in self.app.services:
			label = Gtk.Label(service.getPrettyId())
			grid.attach(label, 0, index, 1, 1)
			
			edit = Gtk.Button(label='Edit')
			edit.plugin = service
			edit.connect('clicked', lambda button: self.showScreen(ScreenPluginEdit, {
				'type': 'service',
				'plugin': button.plugin
			}))
			grid.attach(edit, 1, index, 1, 1)

			delete = Gtk.Button(label='Delete')
			delete.pluginType = 'service'
			delete.plugin = service
			delete.connect('clicked', self.deletePlugin)
			grid.attach(delete, 2, index, 1, 1)

		# outputs list
		label = Gtk.Label('Outputs')
		mainBox.add(label)

		grid = Gtk.Grid()
		grid.set_column_spacing(30)
		grid.set_row_spacing(10)
		mainBox.add(grid)

		index = 0
		for output in self.app.outputs:
			label = Gtk.Label(output.getPrettyId())
			grid.attach(label, 0, index, 1, 1)
			
			edit = Gtk.Button(label='Edit')
			edit.plugin = output
			edit.pluginType = 'service'
			edit.connect('clicked', lambda button: self.showScreen(ScreenPluginEdit, {
				'type': 'output',
				'plugin': button.plugin
			}))
			grid.attach(edit, 1, index, 1, 1)

			delete = Gtk.Button(label='Delete')
			delete.plugin = output
			delete.pluginType = 'output'
			delete.connect('clicked', self.deletePlugin)
			grid.attach(delete, 2, index, 1, 1)

		return mainBox

	def deletePlugin(self, button):
		plugin = button.plugin
		pluginType = button.pluginType

		confirmWindow = Gtk.MessageDialog(
			parent=self, 
			message_type=Gtk.MessageType.QUESTION, 
			buttons=Gtk.ButtonsType.YES_NO,
			message_format='Deleting {name}, are you sure?'.format(name=plugin.getPrettyId())
		)
		confirmWindow.format_secondary_text(
            "Only the {t} configuration will be deleted, not the backups.".format(
            	t=pluginType.capitalize()
        ))

		response = confirmWindow.run()
		if response == Gtk.ResponseType.YES:
			collection = getattr(self.app, utils.getPlural(pluginType))
			collection.remove(plugin)

			self.app.updateConfig()

		confirmWindow.destroy()
		self.showScreen('Home')

	def screenPluginSelect(self, type):
		mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		plugins = getattr(self.app, type + 'Types')

		for name, plugin in plugins.items():
			instance = plugin()

			button = Gtk.Button(label=instance.pretty_name)
			button.plugin = instance.name
			button.connect('clicked', lambda button: self.showScreen(ScreenPluginEdit, {
				'type': type, 
				'plugin': button.plugin
			}))

			mainBox.pack_start(button, True, True, 0)

		cancel = Gtk.Button(label='Cancel')
		cancel.connect('clicked', lambda button: self.showScreen('Home'))
		mainBox.pack_start(cancel, False, False, 0)

		return mainBox

class ScreenRunBackups(Screen):

	def build(self):
		# Check if we can run.
		if not (len(self.app.services) and len(self.app.outputs)):
			dialog = Gtk.MessageDialog(self.app.mainWindow, 0, Gtk.MessageType.INFO,
				Gtk.ButtonsType.OK, "Can not run backups")
			dialog.format_secondary_text(
			    "You have to configure at least one service and one output before running the backups.")
			dialog.run()

			dialog.destroy()

			return False

		# Start running.
		mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		mainBox.add(Gtk.Label('Running Backups...'))
		
		self.mainProgress = progress = Gtk.ProgressBar()
		progress.gui_finished_callback = lambda: self.on_finished()
		progress.set_show_text(True)
		progress.set_text('0/' + str(len(self.app.services)))
		progress.set_fraction(0.0)
		mainBox.pack_start(progress, True, False, 0)

		self.runner = runner = self.app.getRunner()
		handler = runner.progressHandler

		handler.mainProgress = progress
		handler.gui_finished_callback = lambda: self.on_finished()

		runner.start()

		return mainBox

	def on_finished(self):
		self.app.mainWindow.showScreen(ScreenBackupsFinished, data={
			'runner': self.runner
		})

class ScreenBackupsFinished(Screen):

	def build(self):
		mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		mainBox.add(Gtk.Label('Finished all backups'))

		button = Gtk.Button(label='Home')
		button.connect('clicked', lambda button: self.app.mainWindow.showScreen('Home'))

		mainBox.add(button)

		return mainBox

class ScreenPluginEdit(Screen):

	def __init__(self, app, data):
		Screen.__init__(self, app)

		self.pluginType = data['type']
		self.plugin = data['plugin']
		self.isNew = (type(self.plugin) == str)

		self.pluginContainer = app.services if self.pluginType == 'service' else app.outputs

	def build(self):
		"""
		Edit a service.
		If service is a string, it is the service type and a new one 
		will be created.
		If it is a config object, an existing one is edited.
		"""

		if self.isNew:
			# get a fresh instance of the plugin

			if self.pluginType == 'service':
				self.plugin = plugin =  self.app.serviceTypes[self.plugin]()
			elif self.pluginType == 'output':
				self.plugin = plugin =  self.app.outputTypes[self.plugin]()
		else:
			plugin = self.plugin

		mainWidget = mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		mainBox.add(Gtk.Label(plugin.pretty_name))

		form = Gtk.Grid()
		form.set_column_spacing(30)
		form.set_row_spacing(10)

		mainBox.add(form)

		self.fields = fields = {}

		index = 0
		for conf in plugin.config:
			if conf['internal']: continue

			name = conf['name']
			typ = conf['typ']

			value = plugin.getConfigValue(name)

			label = Gtk.Label(name + ':')
			label.set_tooltip_text(conf['description'])
			form.attach(label, 0, index, 1, 1)

			item = None

			if typ == Plugin.TYPE_BOOL:
				item = Gtk.CheckButton()
				item.set_active(value)
			if typ in [Plugin.TYPE_STRING, Plugin.TYPE_NUMBER, Plugin.TYPE_INT, Plugin.TYPE_FLOAT]:

				if conf['options']:
					# Generate a select widget

					store = Gtk.ListStore(str)
					for name, pretty_name in conf['options'].items():
						activeiter = store.append([pretty_name])

					item = Gtk.ComboBox.new_with_model(store)
					renderer = Gtk.CellRendererText()
					item.pack_start(renderer, True)
					item.add_attribute(renderer, "text", 0)
				else:
					# plain text input

					item = Gtk.Entry()
					item.set_text(str(value) if value else '')

			item.set_tooltip_text(conf['description'])

			# set eb property to allow for border spec in save()
			item.eb = None

			fields[name] = item
			form.attach(item, 1, index, 1, 1)

			index += 1

		controlBox = Gtk.Box(spacing=30)
		mainBox.add(controlBox)

		saveButton = Gtk.Button(label='Save')
		saveButton.connect('clicked', self.save)
		controlBox.add(saveButton)

		cancelButton = Gtk.Button(label='Cancel')
		cancelButton.connect('clicked', lambda button: self.app.mainWindow.showScreen('Home'))
		controlBox.add(cancelButton)

		return mainWidget

	def save(self, button):
		data = {}

		allValid = True

		for name, widget in self.fields.items():
			val = None

			if type(widget) == Gtk.Entry:
				val = widget.get_text()
			elif type(widget) == Gtk.CheckButton:
				val = widget.get_active()
			elif type(widget) == Gtk.ComboBox:
				selected = widget.get_active_iter()
				if selected != None:
					model = widget.get_model()
					val = model[selected][0]
			else:
				raise Exception('Unknown widget type')

			data[name] = val

			if not self.plugin.validateField(self.plugin.getConfigItem(name), val):
				allValid = False

				widget.eb = eb = Gtk.EventBox()
				# Gtk.StateType.GTK_STATE_NORMAL
				#eb.modify_bg(Gdk.Color.parse('red'), Gtk.StateType.NORMAL)
				eb.set_border_width(500)
				widget.add(eb)
			else:
				self.plugin.setConfigValue(name, val)

				if widget.eb:
					widget.remove(eb)

		if allValid:
			if self.isNew:
				self.pluginContainer.append(self.plugin)

			self.app.updateConfig()
			self.app.mainWindow.showScreen('Home')

if __name__ == '__main__':
	gui = Gui()
	gui.run()
