import sys
import math
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random as rd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QFont


class Nodo:
    def __init__(self, name, pared, ventana, puerta, ruido, frecuencia):
        self.name = name
        self.pared = pared
        self.ventana = ventana
        self.puerta = puerta
        self.ruido = ruido
        self.frecuencia = frecuencia

    def position(self):
        piso = int(self.name[1])
        habitacion = int(self.name[2:])
        x = piso
        y = habitacion
        z = 0
        return x, y, z

    def calcular_transmision_ruido(self, vecino):
        log_transmision_pared = self.pared - vecino.pared
        log_transmision_ventana = self.ventana - vecino.ventana
        log_transmision_puerta = self.puerta - vecino.puerta
        log_transmision_frecuencia = self.frecuencia

        transmision_total = 10 ** (log_transmision_pared / 10 + log_transmision_ventana / 10 + log_transmision_puerta / 10 + log_transmision_frecuencia / 10)
        transmision_ruido = math.log10(transmision_total)
        return transmision_ruido
    
    def calcular_nivel_ruido(self, vecinos):
        nivel_ruido = self.ruido
        for vecino in vecinos:
            transmision_ruido = self.calcular_transmision_ruido(vecino)
            nivel_ruido += transmision_ruido
        return nivel_ruido

    def calcular_color(self, vecinos):
        ruidos = []
        for vecino in vecinos:
            ruido = self.calcular_nivel_ruido(vecinos)
            ruidos.append(ruido)
        if len(ruidos) == 0:
            return 'green'  
        max_transmision_ruido = max(ruidos)
        if max_transmision_ruido > 80:
            return 'red'
        elif max_transmision_ruido > 60:
            return 'orange'
        elif max_transmision_ruido > 40:
            return 'yellow'
        else:
            return 'green'

    def draw(self, ax, vecinos):
        x, y, z = int(self.name[1]), int(self.name[2]), int(self.name[3])
        dx = 2
        dy = 1
        dz = 2
        color = self.calcular_color(vecinos)
        edgecolor = 'black'
        ax.bar3d(x, y, z, dx, dy, dz, color=color, edgecolor=edgecolor)

class GraphWindow(QWidget):
    def __init__(self, fig):
        super().__init__()
        self.canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Análisis de Niveles de Ruido")
        self.resize(600, 500) 
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.button_results = QPushButton("Mostrar Resultados")
        self.button_results.clicked.connect(self.show_results)
        self.layout.addWidget(self.button_results)
               
        self.button_graph = QPushButton("Mostrar Gráfico")
        self.button_graph.clicked.connect(self.show_graph)
        self.layout.addWidget(self.button_graph)
        
        self.button_exit = QPushButton("Salir")
        self.button_exit.clicked.connect(self.close)
        self.layout.addWidget(self.button_exit)
        
        self.G = nx.Graph()
        self.habitaciones = {}
        self.create_test_case()

    def create_buttons(self):
        self.button_results = QPushButton("Mostrar Resultados", self)
        self.button_results.clicked.connect(self.show_results)
        self.layout.addWidget(self.button_results) 

        self.button_graph = QPushButton("Mostrar Gráfico", self)
        self.button_graph.clicked.connect(self.show_graph)
        self.layout.addWidget(self.button_graph)

        self.button_exit = QPushButton("Salir", self)
        self.button_exit.clicked.connect(self.close)
        self.layout.addWidget(self.button_exit)

    def show_graph(self):
        # Dibuja el grafo
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        for name, habitacion in self.habitaciones.items():
            vecinos = [self.habitaciones[vecino] for vecino in self.G.neighbors(name)]
            habitacion.draw(ax, vecinos)
        ax.set_xlabel('Piso')
        ax.set_ylabel('Habitación')
        ax.set_zlabel('')
        ax.set_title('Niveles de Ruido')

        graph_window = GraphWindow(fig)
        graph_window.setWindowTitle("Gráfico de Niveles de Ruido")

        back_button = QPushButton("Volver", graph_window)
        back_button.clicked.connect(self.show_main_menu)
        back_button.move(10, 10)
        self.setCentralWidget(graph_window)
        graph_window.show()

    def show_main_menu(self):
        self.setCentralWidget(QWidget())
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.create_buttons()
    
    def create_test_case(self):
        habitaciones = {}
        for i in range(3):
            for j in range(2):
                for k in range(2):
                    name = f"P{i+1}{j+1}{k+1}"
                    pared = 20 if j == 0 else 30
                    ventana = 3.3 if k == 0 else 4.3
                    puerta = 1.7
                    ruido = rd.randint(20, 100)
                    frecuencia = rd.randint(10, 80)
                    habitacion = Nodo(name, pared, ventana, puerta, ruido, frecuencia)
                    self.G.add_node(name)
                    habitaciones[name] = habitacion

                    if j < 1:
                        vecino_name = f"P{i+1}{j+2}{k+1}"
                        self.G.add_edge(name, vecino_name)
                    if k < 1:
                        vecino_name = f"P{i+1}{j+1}{k+2}"
                        self.G.add_edge(name, vecino_name)
                    if i < 2:
                        vecino_name = f"P{i+2}{j+1}{k+1}"
                        self.G.add_edge(name, vecino_name)
        
        self.habitaciones = habitaciones

    def show_results(self):
        result = ""
        # Imprime todos los resultados
        for name, habitacion in self.habitaciones.items():
            print('\033[32m-----\n' +f"{name}:"+ '\n-----\033[0m')
            print(f"  Pared Resistencia: {habitacion.pared}")
            print(f"  Ventana Resistencia: {habitacion.ventana}")
            print(f"  Puerta Resistencia: {habitacion.puerta}")
            print(f"  Ruido: \033[36m{habitacion.ruido} Db\033[0m Frecuencia: \033[34m{habitacion.frecuencia} Hz\033[0m")
            vecinos = [self.habitaciones[vecino] for vecino in self.G.neighbors(name)]
            for vecino in vecinos:
                ruido = habitacion.calcular_transmision_ruido(vecino)
                print(f"  Transmisión de ruido a \033[35m{vecino.name}\033[0m (frecuencia: \033[34m{vecino.frecuencia} Hz\033[0m): \033[36m{ruido} Db\033[0m")

        # Imprimir los niveles de ruido de cada nodo
        print('\033[35m' +"\n------------------------------------\nNivel de ruido para cada Habitacion\n------------------------------------"+ '\033[0m')
        nivel_ruido = {}
        for name, habitacion in self.habitaciones.items():
            nivel_ruido[name] = habitacion.calcular_nivel_ruido([self.habitaciones[vecino] for vecino in self.G.neighbors(name)])
            print(f"{name}: {nivel_ruido[name]} dB")

        # Imprime las recomendaciones 
        for name, ruido in nivel_ruido.items():
            print('\033[32m' +f"{name}:\033[0m \033[36m{ruido} dB\033[0m")
            if  ruido <= 70:
                print('\033[35m' +"Recomendación:"+ '\033[0m'+" El nivel de ruido en este nodo es aceptable.\nSin embargo, se pueden tomar medidas adicionales para mejorar\nla habitabilidad, como agregar cortinas gruesas, alfombras o\npaneles acústicos en las paredes.")
            elif 70 < ruido <= 90:
                print('\033[35m' +"Recomendación:"+ '\033[0m'+"  El nivel de ruido en este nodo es moderado.\nSe recomienda tomar medidas para reducir el ruido, como\ninstalar ventanas de doble acristalamiento, utilizar materiales\nde aislamiento acústico en las paredes o colocar alfombras\nabsorbentes de sonido.")
            elif 90 < ruido <= 120:
                print('\033[35m' +"Recomendación:"+ '\033[0m'+"  El nivel de ruido en este nodo es alto y \npuede afectar la habitabilidad.Se sugiere tomar medidas\ninmediatas para reducir el ruido, como utilizar\npaneles insonorizantes en las paredes, puertas y ventanas,\ninstalar sistemas de aislamiento acústico en el techo\ny considerar la reubicación de fuentes de ruido externas.")
            elif ruido > 120:
                print('\033[35m' +"Recomendación:"+ '\033[0m'+"  El nivel de ruido en este nodo está fuera de\nlos rangos establecidos. Se deben realizar mediciones adicionales\ny evaluar las posibles causas del ruido anormal.")
        self.result_label = QLabel(result)
        self.layout.addWidget(self.result_label)
                
 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())