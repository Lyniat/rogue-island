#!/usr/bin/python2
from gi.repository import Gtk


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

    # this signal was added to the glade file so we must have a method for
    # builder.connect.signals to connect to
    def on_mainwindow_destroy(self, object, data=None):
        print "quit with cancel"
        Gtk.main_quit()

if __name__ == "__main__":

    main = main()  # create an instance of our class
    Gtk.main()  # run the darn thing
