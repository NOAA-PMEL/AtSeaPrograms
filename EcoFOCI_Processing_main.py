#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_Processing_main.py
 
 GUI wrapper (using tKinter) for various cruise related processing programs
 
 Purpose:
 --------
  
 
 Usage:
 ------
 All available routines have command line capability as well
 
 Contains:
 ---------
 CTD2NC.py
 

 Original code reference:
 ------------------------

 Built using Anaconda packaged Python:


"""
# System Packages
import datetime, os, sys


# GUI Packages
from PyQt4 import QtGui 

import gui_ui.ecofoci_processing_design as design 
			  # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designer


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 10, 13)
__version__  = "0.2.0"
__status__   = "Development"

class ExampleApp(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.inputButton.clicked.connect(self.input_files)  
        self.processButton.clicked.connect(self.Process_Files)
        self.addMetaButton.clicked.connect(self.AddCruiseMetaData)
        self.btlSummaryButton.clicked.connect(self.BtlSummary)
        self.exitButton.clicked.connect(self.exit_main)

    def input_files(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Pick a folder")
        self.inputList.clear()
        self.outputList.clear()

        if directory: # if user didn't pick a directory don't continue
            self.directory = str(directory)

            for file_name in os.listdir(directory): # for all files, if any, in the directory
                self.inputList.addItem(file_name)  # add file to the listWidget
                self.outputList.addItem(file_name)  # add file to the listWidget

            self.inputButton.setStyleSheet("background-color: green")

           
    def Process_Files(self):
        ''' run data processing routine in file CTD2nc.py'''
        # User Packages
        import OnCruiseRoutines.CTD2NC as CTD2NC
        from OnCruiseRoutines.CTD_Vis import ctd
        from OnCruiseRoutines.CTD_Vis import ncprocessing
        if self.IPHCcheckBox.isChecked():
            rflag = CTD2NC.IPHC_data_processing(os.path.join(self.directory, str(self.inputList.currentItem().text()) + '/'),
                                        os.path.join(self.directory, str(self.outputList.currentItem().text()) + '/'),
                                        pressure_varname=str(self.presscomboBox.currentText()))
        else: #get header info for IPHC style files
            rflag = CTD2NC.data_processing(os.path.join(self.directory, str(self.inputList.currentItem().text()) + '/'),
                                        os.path.join(self.directory, str(self.outputList.currentItem().text()) + '/'),
                                        pressure_varname=str(self.presscomboBox.currentText()))


        if rflag == True:
            self.processButton.setStyleSheet("background-color: green")

    def AddCruiseMetaData(self):
        import PostCruiseRoutines.PostCruiseMetaDBadd as PostCruiseMetaDBadd
        socket.gethostname().split('.')[0]
        rflag = PostCruiseMetaDBadd.AddMeta_fromDB(os.path.join(self.directory, str(self.inputList.currentItem().text()) + '/'),
                                        os.path.join(self.directory, str(self.outputList.currentItem().text()) + '/'),
                                        server=socket)
        if rflag == True:
            self.addMetaButton.setStyleSheet("background-color: green")


    def BtlSummary(self):
        import OnCruiseRoutines.utilities.get_btl as get_btl
        
        rflag = get_btl.report(os.path.join(self.directory, str(self.inputList.currentItem().text()) + '/'),
                                        os.path.join(self.directory, str(self.outputList.currentItem().text()) + '/'))
        if rflag == True:
            self.btlSummaryButton.setStyleSheet("background-color: green")

    def exit_main(self):
        self.close()

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function