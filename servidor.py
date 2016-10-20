import sys
from PyQt4 import QtGui, QtCore, uic
from random import randint 
import uuid
from xmlrpc.server import SimpleXMLRPCServer

class Snake():
    
    def __init__(self):
        self.id = str(uuid.uuid4())[:8]
        rojo = randint(0,255)
        verde = randint(0,255)
        azul = randint(0,255)
        self.color = {"r": rojo, "g": verde, "b": azul}
        self.casillas = []
        self.camino = []
        self.tam = len(self.casillas)
        self.direccion = "Derecha"

    def snake_dic(self):
        dic = {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }
        return dic

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('servidor.ui', self)
        self.setStyleSheet("QMainWindow {background-color: #ACE7EF;}")
        self.pushButton_3.hide()
        self.pushButton.clicked.connect(self.inicia_server)
        self.iniciar = False
        self.pausar = False
        self.timer = None
        self.timer_camino = None 
        self.num_serpientes = []
        self.tabla()
        self.llenar_tab()
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection)
        self.spinBox_2.valueChanged.connect(self.modificar_tabla)
        self.spinBox_3.valueChanged.connect(self.modificar_tabla)
        self.spinBox.valueChanged.connect(self.actualizar_timer)
        self.pushButton_2.clicked.connect(self.comenzar_juego)
        self.pushButton_3.clicked.connect(self.terminar_juego)
        self.show()

    

    def inicia_server(self):
        puerto = self.spinBox_4.value()
        direccion = self.lineEdit.text()
        self.servidor = SimpleXMLRPCServer((direccion, 0))
        puerto = self.servidor.server_address[1] 
        self.spinBox_4.setValue(puerto)
        self.spinBox_4.setReadOnly(True)
        self.lineEdit.setReadOnly(True)
        self.pushButton.setEnabled(False)
        self.servidor.register_function(self.ping)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.timeout = 0
    
    def comenzar_juego(self):
       
        if not self.iniciar:
            self.pushButton_3.show()
            self.snake()
            self.pushButton_2.setText("Pausar el Juego")
            self.dibujar_serpientes()
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.mover_serpientes)
            self.timer.start(150)
            self.timer_camino = QtCore.QTimer(self)
            self.timer_camino.timeout.connect(self.act_camino)
            self.timer_camino.start(100)
            self.tableWidget.installEventFilter(self)
            self.iniciar = True 
        elif self.iniciar and not self.pausar:
            self.timer.stop()
            self.pausar = True
            self.pushButton_2.setText("Reanudar el Juego") 
        elif self.pausar:
            self.timer.start()
            self.pausar = False
            self.pushButton_2.setText("Pausar el Juego")

    def cambia_direccion(self, identificador, numero):
        
        for s in self.num_serpientes:
            if s.id == identificador:
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True 

    def eventFilter(self, source, event):
       
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): 
                key = event.key() 

                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    for serpiente in self.num_serpientes:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    for serpiente in self.num_serpientes:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    for serpiente in self.num_serpientes:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    for serpiente in self.num_serpientes:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event) 

    def snake(self):
        
        serpiente_nueva = Snake()
        creada = False
        while not creada:
            creada = True
            uno = randint(1, self.tableWidget.rowCount()/2)
            dos = uno + 1
            tres = dos +1
            cuatro = tres +1 
            ancho = randint(1, self.tableWidget.columnCount()-1)
            achecar_1, achecar_2, achecar_3, achecar_4 = [uno, ancho], [dos, ancho], [tres, ancho], [cuatro, ancho]
            for s in self.num_serpientes:
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 or achecar_4 in s.casillas:
                    creada = False
                    break
            serpiente_nueva.casillas = [achecar_1, achecar_2, achecar_3, achecar_4]
            self.num_serpientes.append(serpiente_nueva)
            return serpiente_nueva

    def mover_serpientes(self):
        
        for serpiente in self.num_serpientes:
            if self.choca_con_el(serpiente) or self.perdiste(serpiente): 
                self.num_serpientes.remove(serpiente)
                self.llenar_tab()
                serpiente_1 = self.snake()
                self.num_serpientes = [serpiente_1]
            self.tableWidget.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(206, 254, 241))
            x = 0 
            for tupla in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                tupla[0] = serpiente.casillas[x][0]
                tupla[1] = serpiente.casillas[x][1]
            
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.tableWidget.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.tableWidget.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.tableWidget.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.tableWidget.columnCount()-1
        self.dibujar_serpientes() 

    def terminar_juego(self):
        
        self.num_serpientes = []
        self.lcdNumber.display(0)
        self.timer.stop()
        self.iniciar = False
        self.pushButton_3.hide()
        self.pushButton_2.setText("Inicia Juego")
        self.llenar_tab()

    def lista_viboras(self):
        lista = list()
        for serpiente in self.num_serpientes:
            lista.append(serpiente.snake_dic())
        return lista

    def ping(self):
        return "¡Pong!"

    def yo_juego(self):
        
        serpiente_nueva = self.snake()
        diccionario = {"id": serpiente_nueva.id, "color": serpiente_nueva.color}
        return diccionario

    def actualizar_timer(self):
        valor = self.spinBox.value()
        self.timer.setInterval(valor)

    def hacer(self):
        self.servidor.handle_request()

    def estado_del_juego(self):
        
        diccionario = dict()
        diccionario = {
            'espera': self.servidor.timeout, 
            'tamX': self.tableWidget.columnCount(),
            'tamY': self.tableWidget.rowCount(),
            'viboras': self.lista_viboras()
        }
        return diccionario 

    def act_camino(self):
    
        for serpiente in self.serpientes_juego:
            serpiente.camino = []
            for casilla in serpiente.casillas:
                serpiente.camino.append((casilla[0], casilla[1]))

    def actualizar_timer(self):
        valor = self.spinBox.value()
        self.timer.setInterval(valor)

    def dibujar_serpientes(self):
        
        for serpiente in self.num_serpientes:
            for seccion_corporal in serpiente.casillas:
                self.tableWidget.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))


    def choca_con_el(self, serpiente):
        
        for seccion_corporal in serpiente.casillas[0:len(serpiente.casillas)-2]: 
            if serpiente.casillas[-1][0] == seccion_corporal[0] and serpiente.casillas[-1][1] == seccion_corporal[1]:
                return True
        return False

    def perdiste(self, serpiente_a_checar):
        
        for serpiente in self.num_serpientes:
            if serpiente.id != serpiente_a_checar.id:
                for seccion_corporal in serpiente.casillas[:]: 
                    if serpiente_a_checar.casillas[-1][0] == seccion_corporal[0] and serpiente_a_checar.casillas[-1][1] == seccion_corporal[1]:
                        self.num_serpientes.remove(serpiente_a_checar)

    def llenar_tab(self):
       
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(206, 254, 241))

    def tabla(self):
        
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def modificar_tabla(self):
        
        num_filas = self.spinBox_3.value()
        num_columnas = self.spinBox_2.value()
        self.tableWidget.setRowCount(num_filas)
        self.tableWidget.setColumnCount(num_columnas)
        self.llenar_tab()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec_())