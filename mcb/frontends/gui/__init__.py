from pprint import pprint
import sys

from gi.repository import Gtk

from mcb.frontends import Frontend
from mcb import utils
from mcb import Plugin

currentModule = sys.modules[__name__]

class Gui(Frontend):

	def __init__(self):
		self.config = self.getConfig('~/.mycloudbackup')
		self.services = utils.getAllServices()

	def run(self):
		self.mainWindow = win = MainWindow(self)
		win.connect("delete-event", Gtk.main_quit)

		win.showScreen('Home')
		Gtk.main()

class Window(Gtk.Window):

	def __init__(self, app, title):
		Gtk.Window.__init__(self, title=title)
		self.app = app
		self.mainWidget = None

	def showScreen(self, screen, data=None):
		if self.mainWidget:
			self.remove(self.mainWidget)

		if type(screen) == str:
			getattr(self, 'screen' + screen)(data)
		else:
			self.mainWidget = screen(self.app).build(data)

		self.add(self.mainWidget)
		self.show_all()

class Screen(object):

	def __init__(self, app):
		self.app = app

	def build(data):
		# implement in subclass
		pass

class MainWindow(Window):

	def __init__(self, app):
		Window.__init__(self, app, title='MyCloudBackup')

		self.app = app

	def screenHome(self, data=None):
		self.mainWidget = mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		controlBox = Gtk.Box()
		mainBox.add(controlBox)

		# Action buttons
		buttonRun = Gtk.Button(label='Run Backups')
		controlBox.add(buttonRun)

		buttonAdd = Gtk.Button(label='Add Service')
		buttonAdd.connect('clicked', lambda button: self.showScreen('ServiceSelect'))
		controlBox.add(buttonAdd)

		store = Gtk.ListStore(str, str)
		store.append(["The Art of Computer Programming", "Donald E. Knuth"])

		tree = Gtk.TreeView(store)
		mainBox.pack_start(tree, True, True, 0)

		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("Service", renderer, text=0)
		tree.append_column(column)

		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("Last Run", renderer, text=0)
		tree.append_column(column)

		select = tree.get_selection()
		select.connect("changed", self.screenHome_on_service_selected)

	def screenHome_on_service_selected(widget, selection):
	    model, treeiter = selection.get_selected()
	    if treeiter != None:
	        print("You selected", model[treeiter][0])

	def screenServiceSelect(self, data=None):
		self.mainWidget = mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

		for name, service in self.app.services.items():
			instance = service()

			button = Gtk.Button(label=instance.pretty_name)
			button.service = instance.name
			button.connect('clicked', lambda button: self.showScreen(ScreenServiceEdit, button.service))

			mainBox.pack_start(button, True, True, 0)


class ScreenServiceEdit(Screen):

	def build(self, serviceConfig):
		"""
		Edit a service.
		If service is a string, it is the service type and a new one 
		will be created.
		If it is a config object, an existing one is edited.
		"""

		if type(serviceConfig) == str:
			service = self.app.services[serviceConfig]()
		else:
			pass

		mainWidget = mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		mainBox.add(Gtk.Label(service.pretty_name))

		form = Gtk.Grid()
		form.set_column_spacing(30)
		form.set_row_spacing(10)

		mainBox.add(form)

		self.fields = fields = {}

		index = 0
		for conf in service.config:
			if conf['internal']: continue

			name = conf['name']
			typ = conf['typ']

			label = Gtk.Label(name + ':')
			label.set_tooltip_text(conf['description'])
			form.attach(label, 0, index, 1, 1)

			item = None

			if typ == Plugin.TYPE_BOOL:
				item = Gtk.CheckButton()
			if typ in [Plugin.TYPE_STRING, Plugin.TYPE_NUMBER, Plugin.TYPE_INT, Plugin.TYPE_FLOAT]:
				item = Gtk.Entry()
				item.set_text(service.getConfigValue(name, True) or '')

			item.set_tooltip_text(conf['description'])
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
		pass


if __name__ == '__main__':
	gui = Gui()
	gui.run()
