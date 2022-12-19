from tkinter import Frame, BOTH
from pandastable import Table, TableModel
import pandas as pd

class TestApp(Frame):
        """Basic test frame for the table"""
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            #self.main.geometry('600x400+200+100')
            self.main.title('News Sentiment Analyzer')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            df = pd.read_csv('newspaper.csv')
            self.table = pt = Table(f, dataframe=df)
            pt.show()
            return

app = TestApp()
#launch the app
app.mainloop()