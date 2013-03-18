from pprint import pprint
import sys
import logging

from pprint import pprint

from gi.repository import Gtk, Gdk, GObject

from mcb.frontends import Frontend
from mcb import utils
from mcb import Plugin
from mcb import ProgressHandler
from mcb.runner import ThreadRunner

from mcb.frontends.gui.edit import ScreenPluginEdit

currentModule = sys.modules[__name__]

class GuiProgressHandler(ProgressHandler):

	def __init__(self):
		ProgressHandler.__init__(self)
		# list store model that contains data for table
		self.liststore = None
		# iter for currently active backup 
		self.list_iter = None

		# ui update callback after finishing
		self.gui_finished_callback = None

	def onTaskAdded(self, name, progress):
		print("added task: " + name)

	def onTaskActivated(self, name, progress):
		print("Starting task: " + name)
		#self.currentTaksLabel.set_text(name)

	def onProgressChanged(self, name, progress):
		print("Progress: {p}%".format(p=int(progress*100)))
		#self.taskProgress.set_fraction(progress)
		#self.taskProgress.set_text(str(int(progress*100)) + '%')
		Gdk.threads_enter()
		self.liststore[self.list_iter][1] = progress*100
		Gdk.threads_leave()

	def onTaskFinished(self, name, task_progress):
		self.list_iter = self.liststore.iter_next(self.list_iter)
		print("Finished task: " + name)

	def onBackupFinished(self):
		if self.gui_finished_callback:
			self.gui_finished_callback()
		

class Gui(Frontend):

	def __init__(self):
		self.config = self.getConfig('~/.mycloudbackup')

		self.serviceTypes = utils.getAllServices()
		self.services = self.config.getServices()

		self.outputTypes = utils.getAllOutputs()
		self.outputs = self.config.getOutputs()

      	logging.basicConfig(level=logging.DEBUG)

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
		self.currentScreen = None
		self.mainWidget = None


	def showScreen(self, screen, data=None):
		if type(screen) == str:
			print('Showing screen ' + screen)
			widget = getattr(self, 'screen' + screen)(data)
			self.currentScreen = screen
		else:
			print('Showing screen ' + screen.__name__)
			widget = screen(self.app, data).build()
			self.currentScreen = widget

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

	def build(self):
		# implement in subclass
		pass

class MainWindow(Window):

	def __init__(self, app):
		Window.__init__(self, app, title='MyCloudBackup')

		self.app = app
		self.set_border_width(30)
		self.set_default_size(400, 650)

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

			index += 1

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

			index += 1

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
		self.mainBox = mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		mainBox.add(Gtk.Label('Running Backups...'))
		
		self.startButton = startButton = Gtk.Button(label='Start')
		startButton.connect('clicked', lambda button: self.on_start())
		mainBox.add(startButton)
		
		self.runner = runner = self.app.getRunner()
		handler = runner.progressHandler
		
		# Set up the backup list with progressbars
		
		liststore = Gtk.ListStore(str, float)
		first_store_item = None
		
		for service in runner.services:
			list_iter = liststore.append([service.getPrettyId(), 0.0])
			if not first_store_item: first_store_item = list_iter
			
		treeview = Gtk.TreeView(model=liststore)
		mainBox.add(treeview)
			
		renderer_text = Gtk.CellRendererText()
		column_text = Gtk.TreeViewColumn("Text", renderer_text, text=0)
		treeview.append_column(column_text)
		
		renderer_progress = Gtk.CellRendererProgress()
		column_progress = Gtk.TreeViewColumn("Progress", renderer_progress,
            value=1)
		treeview.append_column(column_progress)

		handler.liststore = liststore
		handler.list_iter = first_store_item
		handler.gui_finished_callback = lambda: self.on_finished()

		return mainBox

	def on_start(self):
		self.runner.start()

		# Add an abort button
		self.mainBox.remove(self.startButton)
		self.cancelButton = cancelButton = Gtk.Button(label='Abort')
		cancelButton.connect('clicked', lambda button: self.abort())
		self.mainBox.add(cancelButton)
		self.mainBox.show_all()

	def abort(self):
		pass

	def on_finished(self):
		self.mainBox.remove(self.cancelButton)
		homeButton = Gtk.Button(label='Home')
		homeButton.connect('clicked', lambda button: self.app.mainWindow.showScreen('Home'))
		self.mainBox.add(homeButton)
		self.mainBox.show_all()

class ScreenBackupsFinished(Screen):

	def build(self):
		mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		mainBox.add(Gtk.Label('Finished all backups'))

		button = Gtk.Button(label='Home')
		button.connect('clicked', lambda button: self.app.mainWindow.showScreen('Home'))

		mainBox.add(button)

		return mainBox

if __name__ == '__main__':
	gui = Gui()
	gui.run()
