from gi.repository import Gtk, Gdk, GObject

from mcb import Plugin
from mcb.frontends.gui.base import Screen

class ScreenPluginEdit(Screen):
  """Screen to edit a plugin."""

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
    self.fieldValidLabels = {}

    index = 0
    for conf in plugin.config:
      if conf['internal']: continue

      name = conf['name']
      typ = conf['typ']

      value = plugin.getConfigValue(name)

      label = Gtk.Label(conf['pretty_name'] + ':')
      label.set_tooltip_text(conf['description'])
      form.attach(label, 0, index, 1, 1)

      item = None

      if typ == Plugin.TYPE_BOOL:
        item = Gtk.CheckButton()
        item.set_active(value)
      if typ in [Plugin.TYPE_STRING, Plugin.TYPE_NUMBER, Plugin.TYPE_INT, Plugin.TYPE_FLOAT]:

        if conf['options']:
          # Generate a select widget

          store = Gtk.ListStore(str, str)
          for option_name, pretty_name in conf['options'].items():
            store.append([option_name, pretty_name])

          item = Gtk.ComboBox.new_with_model(store)
          renderer = Gtk.CellRendererText()
          item.pack_start(renderer, True)
          item.add_attribute(renderer, "text", 1)
        else:
          # plain text input

          item = Gtk.Entry()
          field_value = value or conf['default'] or ''
          item.set_text(str(field_value))

      item.set_tooltip_text(conf['description'])

      # set eb property to allow for border spec in save()
      item.eb = None

      fields[name] = item
      form.attach(item, 1, index, 1, 1)

      self.fieldValidLabels[name] = validLabel = Gtk.Label('')
      form.attach(validLabel, 2, index, 1, 1)

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
      print('validating: ' + name)
      print(val)
      if not self.plugin.validateField(self.plugin.getConfigItem(name), val):
        allValid = False

        #widget.eb = eb = Gtk.EventBox()
        # Gtk.StateType.GTK_STATE_NORMAL
        #eb.modify_bg(Gdk.Color.parse('red'), Gtk.StateType.NORMAL)
        #eb.set_border_width(500)
        #widget.add(eb)

        self.fieldValidLabels[name].set_text('!')
        print("Field " + name + " is invalid")
      else:
        self.fieldValidLabels[name].set_text('')
        self.plugin.setConfigValue(name, val)

        if widget.eb:
          widget.remove(widget.eb)

    if allValid:
      if self.isNew:
        self.pluginContainer.append(self.plugin)

      self.app.updateConfig()
      self.app.mainWindow.showScreen('Home')