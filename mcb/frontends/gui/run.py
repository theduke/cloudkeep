from gi.repository import Gtk, Gdk, GObject

from mcb import Plugin
from mcb.frontends.gui import base

class ScreenRunBackups(base.Screen):

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
    
    handler.screen = self
    handler.app = self.app
    handler.liststore = liststore
    handler.list_iter = first_store_item
    handler.gui_finished_callback = lambda: self.on_finished()

    return mainBox
  
  def testDialog(self):
    dialog = Gtk.MessageDialog(self.app.mainWindow, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "Can not run backups")
    dialog.format_secondary_text("Test")
    dialog.run()
    dialog.destroy()

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
    