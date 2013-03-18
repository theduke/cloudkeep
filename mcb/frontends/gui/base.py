'''
Created on Mar 18, 2013

@author: theduke
'''

import sys

from gi.repository import Gtk, Gdk, GObject

from mcb import ProgressHandler

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

