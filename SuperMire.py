# -*- coding: utf-8 -*-

'''SuperMire permet de calculer un niveau +/- 0.00 selon plusieurs côtes.'''


author = 'Lasercata'
last_update = '17.03.2021'
version = '5.0.1'


update_notes = """
SuperMire_v5.0.1 ~~~ 15.09.2020
-------------------------------
Improvements (from v5.0) :
    - Changing the CSV separator from comma (,) to semicolon (;)

**************


SuperMire_v5.0 ~~~ 15.09.2020
-----------------------------
Improvements (from v4.0) :
    - Re-writting the script using classes ;
    - Removing the menu console interface ;
    - Adding the PyQt5 GUI interface ;

    - GUI description :
        .Main window : inputs (nb of cotes, +/- 0.00, cotes) + button calc ;
        .Check window : show the result + button to save

**************


SuperMire_v4.0 ~~~ 10.01.2020
-----------------------------
Improvements (from v3.1) :
    - This list ;
    - The input prompt ends now by '\\n>' (and no more by '\\n>>>') ;
    - When an error occur in a function, it now print the error. (cf to use_menu()) ;

    - Adding function from Cracker_v1.5.1 :
        inp_int ;
        inp_lst ;
        set_prompt ;
        space (from b_cvrt) ;

    - color v3.0 is used, it is smaller (v2) and compatible with Linux ;
    - Replacement of the menu by a function to save hundreds of lines ;
    - Adding ascii art (auth_ascii, SuperMire) ;
    - path is improved (from Cracker_v5.1)) ;

    - Adding the function space from b_cvrt and improving it to space float numbers ;
    - Adding a time function, to write when was it saved, if saved in a file ;
    - Adding simplified function open_f from Cracker_v5.2 to open cotes files ;
    - Some smalls corrections (bugs and other).

**************
"""



##-import
#------gui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import (QIcon, QPixmap, QCloseEvent, QPalette, QColor,
    QStandardItem, QStandardItemModel
)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QLabel,
    QGridLayout, QLineEdit, QMessageBox, QWidget, QPushButton, QCheckBox,
    QHBoxLayout, QVBoxLayout, QGroupBox, QTableWidget, QFileDialog, QTableView,
    QRadioButton, QTextEdit, QSpinBox, QFormLayout, QDoubleSpinBox, QFrame
)

#------others
from os.path import isfile, expanduser
from math import floor
from os import getcwd
import platform
import sys


##-ini
#---------ascii art
auth_ascii_lasercata = """
       _______ _______ _______  ______ _______ _______ _______ _______
|      |_____| |______ |______ |_____/ |       |_____|    |    |_____|
|_____ |     | ______| |______ |    \_ |_____  |     |    |    |     |"""

sp_ascii = """
 _______ _     _  _____  _______  ______ _______ _____  ______ _______
 |______ |     | |_____] |______ |_____/ |  |  |   |   |_____/ |______
 ______| |_____| |       |______ |    \_ |  |  | __|__ |    \_ |______"""



##-Useful functions
def sort(d, key_s=0):
    '''
    Sort a dict of this form :

        d = {
            1: (
                [1, 2, 3],
                [0, 1, 2],
                ...
            ),

            2: (
                [4, 5, 6],
                [3, 4, 5],
                ...
            ),

            ...
        }

    - d : the dict to sort ;
    - key_s : the slice used to sort. Should be an int. Used like that : lambda x: x[key_s].
    '''

    #---Make a list of tuples (with the ex : {1: [(1, 0), (2, 1), (3, 2)], 2: [(4, 3), (5, 4), (6, 5)]}.)
    d1 = trans(d)

    #---Sort it
    d2 = {}
    for k in d1:
        d2[k] = sorted(
            d1[k],
            key=lambda x: x[key_s],
            reverse=True
        )

    #---Remake the dict
    d3 = {}
    for i in d2:
        d3[i] = tuple(
            [[d2[i][j][k] for j in range(len(d2[i]))] for k in range(len(d2[i][0]))]
        )

    return d3


def trans(d):
    '''
    Transform a dict of this form :

        {
            1: (
                [1, 2, 3],
                [0, 1, 2],
            ),

            2: (
                [4, 5, 6],
                [3, 4, 5],
            )
        }

    to a dict of this form :
        {
            1: [
                (1, 0),
                (2, 1),
                (3, 2)
            ],

            2: [
                (4, 3),
                (5, 4),
                (6, 5)
            ]
        }
    '''

    d1 = {}
    for i in d:
        d1[i] = [
            tuple(
                [d[i][j][k] for j in range(len(d[i]))]
            ) for k in range(len(d[i][0]))
        ]

    return d1



##-main
class SuperMire:
    '''Class which define SuperMire's calculation functions'''

    def __init__(self, nb_mires, lvl0_1, prec=3, sep=';'):
        '''
        Initiate SuperMire.

        - nb_mires : the number of mires.
        - lvl0_1 : the level +/- 0.00 according to the first mire ;
        - prec : the precision of the calculated cotes.
        '''

        self.nb_mires = nb_mires
        self.lvl0_1 = lvl0_1
        self.prec = prec
        self.sep = sep

        fdn = ['{0}{0}Côtes de la mire {1} :{0}Côtes calculées de la mire {1} :'.format(sep, k) for k in range(1, nb_mires + 1)]
        self.fdn = ''.join(fdn)



    def _calc_lvl0(self, lst_ptc):
        '''
        Return a dict of the +/- 0.00 for every mire, of this form :
            {1: p0_1, 2: p0_2, ...}

        - lst_ptc : list of all the common points, of this form :
            ({1 : 98, 2 : 206}, {2 : -500, 3 : 201}, {3 : 500, 4 : -60}, ...).
        '''

        lvl0_ = [self.lvl0_1]
        lvl0 = {}

        for j, k in enumerate(lst_ptc):
            lvl0_.append(round(k[j + 2] - k[j + 1] + lvl0_[j - 1], self.prec))

        for j, k in enumerate(lvl0_):
            lvl0[j + 1] = k

        return lvl0


    def _calc_cotes(self, pt0, lst_pt):
        '''
        Calculate the cotes in lst_pt according to the pt0.

        - pt0 : point +/- 0.00 for the mire which has taken the cotes in 'lst_pt' ;
        - lst_pt : the list of the point to calc.

        Return a list containing the calculated cotes.
        '''

        l_calc = []

        for cote in lst_pt:
            l_calc.append(round(pt0 - cote, self.prec))

        return l_calc


    def calc(self, lst_ptc, cotes):
        '''
        Calc the cotes for the mires.

        - lst_ptc : list of all the common points, of this form :
            ({1 : 98, 2 : 206}, {2 : -500, 3 : 201}, {3 : 500, 4 : -60}, ...) ;

        - cotes : the cotes to be calculated, of this form :
            {1: [c1, c2, ...], 2: [c1, c2, ...], ...}, where cx are the cotes.

        Return a dict of the calculated cotes, of this form :
            {1: ([c1, c2, ...], [cc1, cc2, ...]), 2: ([c1, c2, ...], [cc1, cc2, ...]), ...)

        and the +/- 0.00 for each mire :

            return c_cotes, lvl0
        '''

        c_cotes = {}

        lvl0 = self._calc_lvl0(lst_ptc)

        for mire in lvl0:
            c_cotes[mire] = (cotes[mire], self._calc_cotes(lvl0[mire], cotes[mire]))

        self.c_cotes = sort(c_cotes, 1)
        self.lvl0 = lvl0

        return self.c_cotes, lvl0


    def get_csv_str(self):
        '''Return the csv file's content, in str.'''

        try:
            c_cotes_t = trans(self.c_cotes)

        except AttributeError:
            raise Exception('Please run self.crack before this !!!')

        lth_mx = len(max([c_cotes_t[m] for m in c_cotes_t]))

        ret = 'Mire{}+/- 0.00'.format(self.sep)

        for k in range(1, self.nb_mires + 1):
            ret += '\n{}{}{}'.format(k, self.sep, self.lvl0[k])

        ret += '\n' * 3

        ret += self.fdn

        for k in range(lth_mx):
            ret += '\n'

            for mire in range(1, self.nb_mires + 1):
                try:
                    ret += '{0}{0}{1}{0}{2}'.format(self.sep, *c_cotes_t[mire][k]) # ';;{};{}'.format(*c_cotes_t[mire][k])

                except IndexError:
                    ret += self.sep * 3


        return ret


##-GUI
#---------Widgets
#------DoubleCote
class DoubleCote(QGroupBox):
    '''Class which define a Qt widget which allow to get two cotes.'''

    def __init__(self, m, parent=None):
        '''
        Create the widget.

        - m : the nuber of the mire.
        '''

        #------ini
        super().__init__(parent)
        #self.setTitle('Mires {} et {}'.format(m, m + 1))
        self.m = m

        lay = QGridLayout()
        self.setLayout(lay)

        #lay.addWidget(QLabel("Côte d'un point visible depuis les mires {} et {},".format(m, m + 1)), 0, 0, 1, 4)
        lay.addWidget(QLabel('Selon la mire {} :'.format(m)), 1, 0)

        self.c1 = QDoubleSpinBox()
        self.c1.setDecimals(3)
        self.c1.setMinimum(-10**3)
        self.c1.setMaximum(10**3)
        lay.addWidget(self.c1, 1, 1, Qt.AlignLeft)

        lay.addWidget(QLabel('Selon la mire {} :'.format(m + 1)), 2, 0)

        self.c2 = QDoubleSpinBox()
        self.c2.setDecimals(3)
        self.c2.setMinimum(-10**3)
        self.c2.setMaximum(10**3)
        lay.addWidget(self.c2, 2, 1, Qt.AlignLeft)

        self.show()


    def getCotes(self):
        '''
        Return the values of the two QDoubleSpinBox in a dict of this form :
            {m: c1, m + 1: c2}
        '''

        return {self.m: self.c1.value(), self.m + 1: self.c2.value()}


    def clear(self):
        '''Clears the values in the two entries.'''

        self.c1.setValue(0)
        self.c2.setValue(0)


#------AskCotes
class AskCotes(QWidget):
    '''Class which define a Qt widget which allow to get cotes for mire m.'''

    def __init__(self, m, parent=None):
        '''
        Create the widget.

        - m : the nuber of the mire.
        '''

        #------ini
        super().__init__(parent)

        lay = QGridLayout()
        self.setLayout(lay)

        #------widgets
        #---lb
        lay.addWidget(QLabel('Mire n°{}'.format(m)), 0, 0)

        self.table = QSpinTable(5, 1)
        lay.addWidget(self.table, 1, 0)

        self.show()


    def getValues(self):
        '''Return the values of the table in a tuple.'''

        return tuple(self.table.getValues()[0])


#------QSpinTable
class QSpinTable(QWidget):
    '''Class defining a widget which is a table of QDoubleSpinBox.'''

    def __init__(self, row, column, auto_add_row=True, parent=None):
        '''
        Create the widget.

        - row : the number of rows ;
        - column : the number of columns ;
        - auto_add_row : a boolean which indicates if adding automaticly rows
        '''

        #------ini
        super().__init__(parent)

        self.lay = QGridLayout()
        self.setLayout(self.lay)

        if platform.system() == 'Windows':
            mn = 130
            mx = 150

        else:
            mn = 100
            mx = 120

        #------widgets
        self.table = QTableWidget(row, column)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.table.setMaximumWidth(mx)
        self.table.setMinimumWidth(mn)
        self.table.setMinimumHeight(200)

        self.lay.addWidget(self.table, 0, 0)

        for c in range(column):
            for r in range(row):
                wid = QDoubleSpinBox()
                wid.setDecimals(3)
                wid.setMinimum(-10**3)
                wid.setMaximum(10**3)

                self.table.setCellWidget(r, c, wid)

        if auto_add_row:
            self.table.cellWidget(row - 1, 0).valueChanged.connect(self._actualise_rows)


        self.show()


    def addRow(self):
        '''Adds a row at the end of the table.'''

        row_pos = self.table.rowCount()
        nb_col = self.table.columnCount()

        self.table.insertRow(row_pos)

        for c in range(nb_col):
                wid = QDoubleSpinBox()
                wid.setDecimals(3)
                wid.setMinimum(-10**3)
                wid.setMaximum(10**3)

                self.table.setCellWidget(row_pos, c, wid)


    def delRow(self, row=-1):
        '''Delete the row #row. if row == -1, del last row.'''

        if row == -1:
            row = self.table.rowCount() - 1

        self.table.removeRow(row)


    def _actualise_rows(self):
        '''Add or remove a row.'''

        last_row = self.table.rowCount() - 1

        if (self.table.cellWidget(last_row, 0).value() == 0) \
        and (self.table.cellWidget(last_row - 1, 0).value() == 0) \
        and (last_row > 3):
            self.delRow()

        elif self.table.cellWidget(last_row, 0).value() != 0:
            self.addRow()
            self.table.cellWidget(last_row + 1, 0).valueChanged.connect(self._actualise_rows)


    def getValues(self):
        '''Return the table values into a list of lists.'''

        n_rows = self.table.rowCount()
        n_col = self.table.columnCount()

        tb = []

        for col in range(n_col):
            tb.append([])

            for row in range(n_rows):
                tb[col].append(self.table.cellWidget(row, col).value())

        return tb


#------QHLine
class QHLine(QFrame):
    '''Define an horizontal line widget.'''

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)



#------CheckTable
class CheckTable(QMainWindow):
    '''Define the confirmation table popup.'''

    def __init__(self, csv_str, sep=';', parent=None):
        '''Create the window.'''

        #------ini
        super().__init__(parent)
        self.setWindowTitle('Result — SuperMire v' + version)
        self.resize(1000, 500)

        self.csv_str = csv_str
        self.sep = sep
        self.save_path = expanduser('~')

        #------Widgets
        #---main
        self.app_widget = QWidget()
        self.setCentralWidget(self.app_widget)

        main_lay = QGridLayout()
        self.app_widget.setLayout(main_lay)

        #---table
        self.table = QTableView()
        self.table.setMinimumSize(800, 350)
        main_lay.addWidget(self.table, 0, 0)

        self.model = QStandardItemModel(self)
        self.table.setModel(self.model)

        self._set_data()

        #---Buttons
        bt_lay = QHBoxLayout()
        main_lay.addLayout(bt_lay, 1, 0, Qt.AlignRight)

        #-Cancel
        self.bt_cancel = QPushButton('Annuler')
        self.bt_cancel.clicked.connect(self.close)
        bt_lay.addWidget(self.bt_cancel)

        #-Saving
        self.bt_save = QPushButton('Enregistrer ...')
        self.bt_save.clicked.connect(self.save)
        bt_lay.addWidget(self.bt_save)


    def _set_data(self):
        '''Set the csv data into the table.'''

        lines = self.csv_str.split('\n')
        tb = []

        for l in lines:
            tb.append(l.split(self.sep))

        for row in tb:
            self.model.appendRow([QStandardItem(k) for k in row])

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


    def _get_data(self):
        '''Return the table data in a csv format.'''

        n_rows = self.model.rowCount()
        n_col = self.model.columnCount()

        ret = ''

        for row in range(n_rows):
            for col in range(n_col):
                data = self.model.data(self.model.index(row, col))
                ret += (data, '')[data == None] + self.sep

            ret += '\n'

        return ret



    def save(self):
        '''Save the result in a csv file.'''

        fn = QFileDialog.getSaveFileName(self, 'Enregistrer les côtes — SuperMire v' + version, self.save_path, 'Fichiers CSV(*.csv);;Tous les fichiers(*)')[0]

        self.save_path = fn.replace('\\', '/')[:-len(fn.replace('\\', '/').split('/')[-1])]

        if fn in ((), ''):
            return -3 #Canceled

        if not '.csv' in fn:
            fn += '.csv'

        with open(fn, 'w', encoding='utf-8') as f:
            f.write(self._get_data())

        QMessageBox.about(None, 'Fait !','<h2>Vos côtes ont bien étés enregistées dans le fichier "{}" !</h2>'.format(fn.replace('\\', '/').split('/')[-1]))


    def use(csv_str, sep=';', parent=None):
        '''launch the window'''

        win_chk = CheckTable(csv_str, sep, parent)
        win_chk.show()


#todo: be able to open a csv file and modify it ?


#---------SuperMireGui
class SuperMireGui(QMainWindow):
    '''Define the SuperMire's GUI.'''

    def __init__(self, max_mires=10, parent=None):
        '''Create the window'''

        #------ini
        super().__init__(parent)
        self.setWindowTitle('SuperMire v' + version)

        try:
            self.setWindowIcon(QIcon('SuperMire.ico'))

        except:
            pass

        self.max_mires = max_mires


        #------Widgets
        #---main
        self.app_widget = QWidget()
        self.setCentralWidget(self.app_widget)

        self.main_lay = QGridLayout()
        self.app_widget.setLayout(self.main_lay)

        #---base data
        self.mire_wid = QWidget()
        mire_lay = QGridLayout()
        self.mire_wid.setLayout(mire_lay)
        self.main_lay.addWidget(self.mire_wid, 0, 0, 1, 5)#, Qt.AlignTop, Qt.AlignCenter)

        #-nb mires
        mire_lay.addWidget(QLabel('Nombre de mires :'), 0, 0, Qt.AlignRight)

        self.nb_mires = QSpinBox()
        self.nb_mires.setMaximum(max_mires)
        self.nb_mires.setMinimum(1)
        self.nb_mires.setValue(2)
        self.nb_mires.valueChanged.connect(self.db_mires)
        self.nb_mires.valueChanged.connect(self.set_cotes)
        mire_lay.addWidget(self.nb_mires, 0, 1, Qt.AlignLeft)

        #-+/- 0.00 from mire 1
        mire_lay.addWidget(QLabel('+/- 0.00 depuis la mire 1 :'), 1, 0, Qt.AlignRight)

        self.pt0_m1 = QDoubleSpinBox()
        self.pt0_m1.setDecimals(3)
        self.pt0_m1.setMinimum(-10**3)
        self.pt0_m1.setMaximum(10**3)
        mire_lay.addWidget(self.pt0_m1, 1, 1, Qt.AlignLeft)


        self.sep_1 = QHLine()
        self.main_lay.addWidget(self.sep_1, 1, 0, 1, -1)


        #---common points
        cm_pt_lay = QGridLayout()
        self.main_lay.addLayout(cm_pt_lay, 2, 0)

        self.common_pt_lb = QLabel('Point communs visibles depuis deux mires :')
        cm_pt_lay.addWidget(self.common_pt_lb, 0, 0)

        self.double_mires = {}
        for m in range(max_mires - 1):
            self.double_mires[m + 1] = DoubleCote(m + 1)
            cm_pt_lay.addWidget(self.double_mires[m + 1], m // 3 + 1, m % 3)# m % 3 + 3, m // 3)

        self.db_mires(2)


        self.main_lay.addWidget(QHLine(), 3, 0, 1, -1)


        #---Cotes
        cotes_lay = QGridLayout()
        self.main_lay.addLayout(cotes_lay, 4, 0)

        cotes_lay.addWidget(QLabel('Côtes :'), 0, 0)

        self.cotes_mires = {}
        for m in range(1, max_mires + 1):
            self.cotes_mires[m] = AskCotes(m)
            cotes_lay.addWidget(self.cotes_mires[m], 1, m - 1, -1, 1)

        self.set_cotes(2)


        #---Calc button
        self.bt_calc = QPushButton('Calculer')
        self.bt_calc.clicked.connect(self.calc)
        self.main_lay.addWidget(self.bt_calc, 5, 0, Qt.AlignRight)


    def db_mires(self, nb_m):
        '''Actualise the widgets with the mires.'''

        if nb_m == 1:
            for w in (self.common_pt_lb, self.sep_1):
                w.hide()

        else:
            for w in (self.common_pt_lb, self.sep_1):
                w.show()


        for m in range(1, 10): # Hide all the widgets,
            self.double_mires[m].hide()

        for m in range(1, nb_m): # and only show asked ones.
            self.double_mires[m].show()


    def set_cotes(self, nb_m):
        '''Actualise the cotes widgets'''

        for m in range(1, 11): # Hide all the widgets,
            self.cotes_mires[m].hide()

        for m in range(1, nb_m + 1): # and only show asked ones.
            self.cotes_mires[m].show()

        self.resize(0, 0)



    def calc(self):
        '''
        Get all the data from the GUI, use the SuperMire class to calculate
        the cotes.
        '''

        #------Get data
        #---Main
        nb_mires = self.nb_mires.value()
        pt0_m1 = self.pt0_m1.value()

        #---Common points
        lst_ptc = []
        for m in range(2, nb_mires + 1):
            lst_ptc.append(self.double_mires[m - 1].getCotes())

        #---Cotes
        cotes = {}
        for m in range(1, nb_mires + 1):
            cotes[m] = self.cotes_mires[m].getValues()


        #------Calculate
        sm = SuperMire(nb_mires, pt0_m1)
        c_cotes, lvl0 = sm.calc(lst_ptc, cotes)


        #------Save
        csv_str = sm.get_csv_str()

        CheckTable.use(csv_str, parent=self)


    #---------use
    def use():
        '''Launch the application.'''

        global app, win

        app = QApplication(sys.argv)
        win = SuperMireGui()
        win.show()

        sys.exit(app.exec_())



##-run
if __name__ == '__main__':
    SuperMireGui.use()

