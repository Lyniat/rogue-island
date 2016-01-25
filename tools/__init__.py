#!/usr/bin/python2
from gi.repository import Gtk
import shelve

app = None
path = None

# GUI panel at the bottom/top/side of the screen
bottom_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
top_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT_TOP)
side_panel = libtcod.console_new(SIDE_PANEL_WIDTH, SIDE_PANEL_HEIGHT)
numKlicks = 0
time = 0

class main:
    def __init__(self):
        self.builder = Gtk.Builder()  # create an instance of the gtk.Builder
        self.builder.add_from_file('data/glade_editor.glade')  # add the xml file to the Builder
        self.builder.connect_signals(self)  # connect the signals added in the glade file
        self.window = self.builder.get_object("MainWindow")  # This gets the 'window1' object

        # adding a tab to the notebook and inserting an object
        # get an instance of the notebook
        self.notebook = self.builder.get_object('MainNotebook')

        self.window.show_all()  # this shows all the objects
        self.notebook.set_current_page(0)  # set the current page after showing

        global app
        app = self.builder

    # this signal was added to the glade file so we must have a method for
    # builder.connect.signals to connect to
    def on_mainwindow_destroy(self, object, data=None):
        print "quit with cancel"
        Gtk.main_quit()

    def on_select_save(self, menuitem, data=None):
        print("save clicked")
        self.save_player()

    def on_select_open(self, menuitem, data=None):
        dialog = Gtk.FileChooserDialog("Select File", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            print("Open clicked")
            print("File selected: " + filepath)
            self.load_player(filepath)
            global path
            path = filepath
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def load_player(self, path):
        file = shelve.open(path, 'r')
        player_race = file['player_race']
        player_gender = file['player_gender']
        player_first_name = file['player_first_name']
        player_name = file['player_name']

        player_hp = file['player_hp']

        file.close()

        element = app.get_object("PlayerRaceCombobox")
        if player_race == "human":
            element.set_active(0)
        elif player_race == "elf":
            element.set_active(1)
        elif player_race == "dwarf":
            element.set_active(2)

        element = app.get_object("PlayerGenderCombobox")
        if player_gender == "m":
            element.set_active(0)
        else:
            element.set_active(1)

        element = app.get_object("PlayerFirstNameEntry")
        element.set_text(player_first_name)

        element = app.get_object("PlayerNameEntry")
        element.set_text(player_name)

        element = app.get_object("PlayerHPEntry")
        element.set_text(str(player_hp))

    def save_player(self):
        file = shelve.open(path, 'n')
        element = app.get_object("PlayerRaceCombobox")
        if element.get_active() == 0:
            file['player_race'] = "human"
        elif element.get_active() == 1:
            file['player_race'] = "elf"
        elif element.get_active() == 2:
            file['player_race'] = "dwarf"

        element = app.get_object("PlayerGenderCombobox")
        if element.get_active() == 0:
            file['player_gender'] = "m"
        else:
            file['player_gender'] = "f"

        element = app.get_object("PlayerFirstNameEntry")
        file['player_first_name'] = element.get_text()

        element = app.get_object("PlayerNameEntry")
        file['player_name'] = element.get_text()

        element = app.get_object("PlayerHPEntry")
        file['player_hp'] = element.get_text()

        file.close()

if __name__ == "__main__":
    main = main()  # create an instance of our class
    Gtk.main()  # run the darn thing
