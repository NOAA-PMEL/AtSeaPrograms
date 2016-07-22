#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_Processing.py
 
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
import datetime, os

# User Packages
from OnCruiseRoutines.CTD_Vis import ctd
from OnCruiseRoutines.CTD_Vis import ncprocessing

# GUI Packages
import Tkinter as tk
import tkMessageBox


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 10, 13)
__version__  = "0.2.0"
__status__   = "Development"

"""------------------------------- tkinter GUI--------------------------------------------"""
class ExampleApp(tk.Frame):

    def __init__(self, master):
        # Initialize window using the parent's constructor
        tk.Frame.__init__(self,
                          master)
        # Set the title
        self.master.title('Seabird CTD Processing to ECOFOCI Archive')
 
        # This allows the size specification to take effect
        self.pack_propagate(0)
        
        # We'll use the flexible pack layout manager
        self.pack()
        
        #center the windo
        self.centerWindow()


        #define buttons
        self.input_button = tk.Button(self, text ="Path to Cruise .cnv files", command = self.input_dir)
        self.output_button = tk.Button(self, text ="Path to save processed files", command = self.output_dir)
        self.exit_button = tk.Button(self, text ="Exit", command = self.exit_prog)
        self.process_button = tk.Button(self, text ="Process Files", command = self.file_processing)
        self.meta_add_button = tk.Button(self, text ="Add Cruise Meta Information", command = self.AddCruiseMetaData)
        self.strip_epic_button = tk.Button(self, text ="Strip non EPIC vars", command = self.StripEPIC)
        self.btl_summary_button = tk.Button(self, text ="Generate Bottle Summary", command = self.btlSummary)
        self.btl_archive_button = tk.Button(self, text ="Generate Bottle Archive", command = self.btlArchive)

        # Put the controls on the form
        self.exit_button.grid(row=7, column=0, sticky='w')
        self.btl_archive_button.grid(row=6, column=0, sticky='w')
        self.btl_summary_button.grid(row=5, column=0, sticky='w')
        self.strip_epic_button.grid(row=4, column=0, sticky='w')
        self.meta_add_button.grid(row=3, column=0, sticky='w')
        self.process_button.grid(row=2, column=0, sticky='w')
        self.output_button.grid(row=1, column=0, sticky='w')
        self.input_button.grid(row=0, column=0, sticky='w')
        
        
    def input_dir(self):
        from tkCommonDialog import Dialog
        self.input_dir = Dialog()
        self.input_dir.command = "tk_chooseDirectory"
        self.input_dir.__init__()
        self.input_dir = self.input_dir.show()
        self.input_dir = str(self.input_dir) + '/'
        # Put output on the form
        tk.Label(self, text=self.input_dir).grid(row=0, column=1, sticky='e')
        self.update()
        
    def output_dir(self):
        from tkCommonDialog import Dialog
        self.output_dir = Dialog()
        self.output_dir.command = "tk_chooseDirectory"
        self.output_dir.__init__()
        self.output_dir = self.output_dir.show()
        self.output_dir = str(self.output_dir) + '/'
        # Put output on the form
        tk.Label(self, text=self.output_dir).grid(row=1, column=1, sticky='e')
        self.update()
        
    def file_processing(self):
        ''' run data processing routine in file CTD2nc.py'''
        import OnCruiseRoutines.CTD2NC as CTD2NC
        
        rflag = CTD2NC.data_processing(self.input_dir, self.output_dir)
        if rflag == True:
            tk.Label(self, text="Complete").grid(row=2, column=1, sticky='e')
            self.update()
        
    def AddCruiseMetaData(self):
        import PostCruiseRoutines.PostCruiseMetaDBadd as PostCruiseMetaDBadd
        
        rflag = PostCruiseMetaDBadd.AddMeta_fromDB(self.input_dir, self.output_dir)
        if rflag == True:
            tk.Label(self, text="Complete").grid(row=3, column=1, sticky='e')
            self.update()

    def StripEPIC(self):
        import PostCruiseRoutines.StripEPIC as StripEPIC

        rflag = StripEPIC.StripEPIC(self.input_dir, self.output_dir)
        if rflag == True:
            tk.Label(self, text="Complete").grid(row=4, column=1, sticky='e')
            self.update()
        
    def btlSummary(self):
        import OnCruiseRoutines.utilities.get_btl as get_btl
        
        rflag = get_btl.report(self.input_dir, self.output_dir)
        if rflag == True:
            tk.Label(self, text="Complete").grid(row=5, column=1, sticky='e')
            self.update()

    def btlArchive(self):
        #import PostCruiseRoutines.NCbtl_create.get_btl as get_btl

        rflag = get_btl.report(self.input_dir, self.output_dir)
        if rflag == True:
            tk.Label(self, text="Complete").grid(row=6, column=1, sticky='e')
            self.update()        

            
    def exit_prog(self):
        self.quit()
        
    def centerWindow(self):
      
        w = 750
        h = 250

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def run(self):
        ''' Run the app '''
        self.mainloop()

"""------------------------------------------------------------------------------------"""

        
app = ExampleApp(tk.Tk())
app.run()