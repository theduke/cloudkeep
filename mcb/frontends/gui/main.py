import logging

from gi.repository import Gtk, Gdk, GObject

from mcb import utils

from mcb.frontends import Frontend

from mcb.runner import ThreadRunner

from mcb.frontends.gui.base import Window, GuiProgressHandler
from mcb.frontends.gui.run import ScreenRunBackups
from mcb.frontends.gui.edit import ScreenPluginEdit

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
    
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()

  def updateConfig(self):
    self.config.importServices(self.services)
    self.config.importOutputs(self.outputs)

    self.config.toFile()

  def getRunner(self):
    handler = GuiProgressHandler()

    runner = ThreadRunner(self.config)
    runner.setProgressHandler(handler)

    return runner

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
  
if __name__ == '__main__':
  gui = Gui()
  gui.run()