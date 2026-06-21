import tkinter as tk
import pygame
import sys

from game_logic import Juego, FILAS, COLUMNAS

# =====================================================================
# CONFIGURACION GENERAL
# =====================================================================
<<<<<<< HEAD:pro.py
TAM_CELDA = 38
MARGEN = 2
=======
# Variables para la configuración de la grilla, flota y bombas especiales
FILAS = COLUMNAS = 10
FLOTA = [4, 3, 2, 2] # tamaños de los barcos de cada jugador
BOMBAS_CRUZ = 3 # bombas en cruz disponibles por jugador
>>>>>>> main:Codigo/BatallaNaval.py

# Variables para la definición de la resolución de la pantalla
ANCHO = 900 # ancho
ALTO = 660 # alto
MARGEN = 2 # tamaño recuadro de las celdas en ambas grillas

# Variables utilizadas para dimensionar la grilla objetivo
GRID_X = 320 # esquina superior izquierda de la grilla objetivo
GRID_Y = 150
TAM_CELDA = 38 # tamaño celda grilla objetivo

# Variables utilizadas para dimensionar la mini grilla
MINIGRID_X = 40 # esquina superior izquierda de la grilla propia
MINIGRID_Y = 500
MINITAM_CELDA = 6 # tamaño celda grilla propia

# Variables utilizadas para verificación de comportamiento 
mostrarSusBarcos = 0 # muestra Barcos del Objetivo en grilla en color Verde
mostrarMisBarcos = 0 # muestra Barcos propios en minigrilla en color Verde

# Colores utilizados para representación de estados de celdas en grillas
DESCONOCIDO = (41, 128, 185) # celda no disparada (niebla)
BARQUITO = (46, 204, 113) # color utilizado para mostrar los barcos en las grillas
AGUA = (149, 165, 166)  
TOCADO = (231, 76, 60)  
# Otros colores utilizados
FONDO = (18, 32, 47)
PANEL = (27, 47, 66)
BLANCO = (236, 240, 241)
GRIS = (127, 140, 141)
VERDE = (46, 204, 113)
AMARILLO = (241, 196, 15)
BTN = (52, 73, 94)
BTN_SEL = (41, 128, 185)

# =====================================================================
<<<<<<< HEAD:pro.py
# DIBUJO
# =====================================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Batalla Naval Multijugador")
fuente   = pygame.font.SysFont("Arial", 20)
fuente_b = pygame.font.SysFont("Arial", 26, bold=True)
fuente_p = pygame.font.SysFont("Arial", 16)


def texto(txt, x, y, f=fuente, color=BLANCO, centrado=False):
    #esta cosa recibe el texto que querés poner en pantalla, las coordenadas, 
    #la fuente, el color y la posición en pantalla
=======
# Inicializacion de pantalla grafica, fuente y titulos
# =====================================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Batalla Naval Multijugador")
fuente = pygame.font.SysFont("Arial", 20)
fuente_b = pygame.font.SysFont("Arial", 26, bold=True)
fuente_p = pygame.font.SysFont("Arial", 16)

# =====================================================================
# MODELO: TABLERO
# =====================================================================
class Tablero:
    def __init__(self): # Constructor de la clase tablero
        self.barcos = [[0] * COLUMNAS for i in range(FILAS)] # 1 = hay barco
        self.disparos = [[None] * COLUMNAS for j in range(FILAS)] # None / 'agua' / 'tocado'
        self.celdas_barco = 0
        self._colocar_flota()

    def _colocar_flota(self): # Funcion para generar distribución de las flotas
        for tam in FLOTA:
            colocado = False
            while not colocado:
                horizontal = random.choice([True, False])
                if horizontal:
                    f = random.randint(0, FILAS - 1)
                    c = random.randint(0, COLUMNAS - tam)
                    celdas = [(f, c + i) for i in range(tam)]
                else:
                    f = random.randint(0, FILAS - tam)
                    c = random.randint(0, COLUMNAS - 1)
                    celdas = [(f + i, c) for i in range(tam)]
                if all(self.barcos[ff][cc] == 0 for ff, cc in celdas):
                    for ff, cc in celdas:
                        self.barcos[ff][cc] = 1
                    self.celdas_barco += tam
                    colocado = True

    def recibir_disparo(self, f, c): # Funcion para reflejar el disparo en la grilla
        """Devuelve 'agua', 'tocado' o 'repetido'."""
        if self.disparos[f][c] is not None:
            return 'repetido'
        if self.barcos[f][c] == 1:
            self.disparos[f][c] = 'tocado'
            self.celdas_barco -= 1
            return 'tocado'
        self.disparos[f][c] = 'agua'
        return 'agua'

    @property # Decorador para determinar que no hay mas barcos en el objetivo
    def hundido(self):
        return self.celdas_barco <= 0

# =====================================================================
# MODELO: JUGADOR
# =====================================================================
class Jugador: 
    def __init__(self, numero): # Contructor de Jugador con numero, tablero, bombas disponibles y estado
        self.numero = numero
        self.nombre = f"Jugador {numero}"
        self.tablero = Tablero()
        self.bombas = BOMBAS_CRUZ
        self.vivo = True


# =====================================================================
# LOGICA DE PARTIDA
# =====================================================================
class Juego:
    def __init__(self, cantidad): # Contructor de Juego con todos los jugadores
        self.jugadores = [Jugador(i + 1) for i in range(cantidad)]
        self.turno = 0 # indice del jugador actual
        self.modo = 'simple' # 'simple' o 'bomba'
        self.objetivo = None # indice del jugador objetivo
        self.mensaje = "" # primera linea de mensaje a mostrar en panel
        self.mensaje2 = "" # segunda linea de mensaje a mostrar en panel
        self._elegir_objetivo_inicial() # se elige el primer objetivo

    @property
    def actual(self):
        return self.jugadores[self.turno]

    def vivos(self):
        return [j for j in self.jugadores if j.vivo]

    def oponentes(self):
        return [j for j in self.jugadores if j.vivo and j is not self.actual]

    def _elegir_objetivo_inicial(self):
        ops = self.oponentes()
        self.objetivo = self.jugadores.index(ops[0]) if ops else None

    def disparar(self, f, c):
        """Aplica el ataque. Devuelve True si el turno se consumio."""
        objetivo = self.jugadores[self.objetivo]

        if self.modo == 'bomba' and self.actual.bombas > 0:
            celdas = [(f, c), (f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]
            celdas = [(ff, cc) for ff, cc in celdas
                      if 0 <= ff < FILAS and 0 <= cc < COLUMNAS]
            resultados = [objetivo.tablero.recibir_disparo(ff, cc) for ff, cc in celdas]
            if all(r == 'repetido' for r in resultados):
                self.mensaje = "Toda la zona ya fue atacada."
                return False
            self.actual.bombas -= 1
            tocados = resultados.count('tocado')
            self.mensaje = f"Bomba en cruz: {tocados} impacto(s)."
        else:
            resultado = objetivo.tablero.recibir_disparo(f, c)
            if resultado == 'repetido':
                self.mensaje = "Esa celda ya fue disparada."
                return False
            self.mensaje = "¡Impacto!" if resultado == 'tocado' else "Agua."

        if objetivo.tablero.hundido:
            objetivo.vivo = False
            self.mensaje2 = f"{objetivo.nombre} fue eliminado."
        return True

    def avanzar_turno(self):
        time.sleep(1)
        for _ in range(len(self.jugadores)):
            self.turno = (self.turno + 1) % len(self.jugadores)
            if self.actual.vivo:
                break
        self.modo = 'simple'
        self.mensaje = ""
        self.mensaje2 = ""
        self._elegir_objetivo_inicial()

    def ganador(self):
        v = self.vivos()
        return v[0] if len(v) == 1 else None

# =====================================================================
# FUNCIONES AUXILIARES PARA MOSTRAR PANTALLAS
# =====================================================================
def texto(txt, x, y, f=fuente, color=BLANCO, centrado=False): # Renderiza texto a imprimir
>>>>>>> main:Codigo/BatallaNaval.py
    img = f.render(txt, True, color)
    rect = img.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    pantalla.blit(img, rect)


def dibujar_grilla(juego): # Dibuja grilla objetivo
    objetivo = juego.jugadores[juego.objetivo]
    texto(f"Disparar contra: {objetivo.nombre}", GRID_X, GRID_Y - 35, fuente_b, AMARILLO)
    for f in range(FILAS):
        for c in range(COLUMNAS):
            estado = objetivo.tablero.disparos[f][c]
            if estado == 'tocado':
                color = TOCADO
            elif estado == 'agua':
                color = AGUA
            else:
                estado = objetivo.tablero.barcos[f][c]
                if estado == 1 and mostrarSusBarcos == 1:
                     color = BARQUITO
                else:
                     color = DESCONOCIDO
            x = GRID_X + c * (TAM_CELDA + MARGEN)
            y = GRID_Y + f * (TAM_CELDA + MARGEN)
            pygame.draw.rect(pantalla, color, (x, y, TAM_CELDA, TAM_CELDA))

def dibujar_minigrilla(juego): # Dibuja minigrilla del panel del jugador actual
    griactual = juego.jugadores[juego.turno]
    texto(f"Grilla: {griactual.nombre}", MINIGRID_X, MINIGRID_Y - 35, fuente_b, AMARILLO)
    for f in range(FILAS):
        for c in range(COLUMNAS):
            estado = griactual.tablero.disparos[f][c]
            if estado == 'tocado':
                color = TOCADO
            elif estado == 'agua':
                color = AGUA
            else:
                estado = griactual.tablero.barcos[f][c]
                if estado == 1 and mostrarMisBarcos == 1:
                     color = BARQUITO
                else:
                     color = DESCONOCIDO

            x = MINIGRID_X + c * (MINITAM_CELDA + MARGEN)
            y = MINIGRID_Y + f * (MINITAM_CELDA + MARGEN)
            pygame.draw.rect(pantalla, color, (x, y, MINITAM_CELDA, MINITAM_CELDA))

def dibujar_panel(juego, botones_obj, btn_modo): # Dibuja panel con información del jugador actual
    pygame.draw.rect(pantalla, PANEL, (0, 0, 300, ALTO))
    texto(juego.actual.nombre, 20, 25, fuente_b, VERDE)
    texto(f"Bombas en cruz: {juego.actual.bombas}", 20, 70, fuente_p)

    modo_txt = "BOMBA EN CRUZ" if juego.modo == 'bomba' else "DISPARO SIMPLE"
    pygame.draw.rect(pantalla, BTN_SEL if juego.modo == 'bomba' else BTN, btn_modo)
    texto(modo_txt, btn_modo.centerx, btn_modo.centery, fuente_p, BLANCO, centrado=True)

    texto("Atacar a:", 20, 185, fuente)
    for rect, idx in botones_obj:
        sel = (idx == juego.objetivo)
        pygame.draw.rect(pantalla, BTN_SEL if sel else BTN, rect)
        texto(juego.jugadores[idx].nombre, rect.centerx, rect.centery,
              fuente_p, BLANCO, centrado=True)

    texto(juego.mensaje, 20, ALTO - 60, fuente_p, AMARILLO)
    texto(juego.mensaje2, 20, ALTO - 40, fuente_p, AMARILLO)


<<<<<<< HEAD:pro.py
def construir_botones(juego):
    botones_obj = [] # HACen referencia al jugador al que le vas a pregar
=======
def construir_botones(juego): # Muestra los botones diponibles de oponentes
    botones_obj = []
>>>>>>> main:Codigo/BatallaNaval.py
    y = 215
    for j in juego.oponentes():
        idx = juego.jugadores.index(j)
        botones_obj.append((pygame.Rect(20, y, 200, 36), idx))
        y += 44
    btn_modo = pygame.Rect(20, 100, 200, 36)
    return botones_obj, btn_modo


def celda_desde_mouse(pos): # Determina celda a partir de la posicion del mouse
    mx, my = pos
    c = (mx - GRID_X) // (TAM_CELDA + MARGEN) # Usamos la doble barra para ahorrarnos el floor.
    f = (my - GRID_Y) // (TAM_CELDA + MARGEN)
    if 0 <= f < FILAS and 0 <= c < COLUMNAS:
        return int(f), int(c)
    return None


# =====================================================================
# PANTALLAS (estados): config -> handoff -> jugando -> fin
# =====================================================================
def pantalla_config():
    cantidad = 2
    while True:
        pantalla.fill(FONDO)
        texto("SUPER BATALLA NAVAL", ANCHO // 2, 120, fuente_b, BLANCO, centrado=True)
        texto("¿Cuantos jugadores?", ANCHO // 2, 200, fuente, BLANCO, centrado=True)
        texto(str(cantidad), ANCHO // 2, 270, fuente_b, AMARILLO, centrado=True)
        texto("← / → para cambiar | ENTER para empezar",
              ANCHO // 2, 360, fuente_p, GRIS, centrado=True)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT and cantidad < 6:
                       cantidad += 1
                elif e.key == pygame.K_LEFT and cantidad > 2:
                    cantidad -= 1
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return cantidad


def pantalla_handoff(juego):
    while True:
        pantalla.fill(FONDO)
        texto(f"Turno de {juego.actual.nombre}", ANCHO // 2, ALTO // 2 - 30,
              fuente_b, VERDE, centrado=True)
        texto("Click para comenzar tu turno", ANCHO // 2, ALTO // 2 + 30,
              fuente_p, GRIS, centrado=True)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                return


def pantalla_fin(ganador):
    while True:
        pantalla.fill(FONDO)
        texto("¡VICTORIA!", ANCHO // 2, ALTO // 2 - 40, fuente_b, AMARILLO, centrado=True)
        texto(f"{ganador.nombre} hundio a toda la flota enemiga.",
              ANCHO // 2, ALTO // 2 + 20, fuente, BLANCO, centrado=True)
        texto(f"{ganador.nombre} presione ESC para terminar",
              ANCHO // 2, ALTO // 2 + 40, fuente, BLANCO, centrado=True)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

# Arranca el juego
def main():
<<<<<<< HEAD:pro.py
    cantidad = pantalla_config()
    juego = Juego(cantidad) #Cantidad es cantidad de jugadores, nada de muchos juegos eh
    pantalla_handoff(juego)

    while True:
        ganador = juego.ganador() # Devuelve el array de jugadores que están vivos, si hay uno solo, es el ganador
=======
    cantidad = pantalla_config() #Definición de cantidad de jugadores
    juego = Juego(cantidad)
    pantalla_handoff(juego) #Pantalla para evitar ver la grilla del otro jugador

    while True:
        ganador = juego.ganador() # Verifica si hay un ganador
>>>>>>> main:Codigo/BatallaNaval.py
        if ganador:
            time.sleep(2)
            pantalla_fin(ganador) # Muestra pantalla final con el ganador

        # Comienza a armar pantalla principal
        botones_obj, btn_modo = construir_botones(juego)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                # ¿clic en boton de modo?
                if btn_modo.collidepoint(e.pos) and juego.actual.bombas > 0:
                    juego.modo = 'bomba' if juego.modo == 'simple' else 'simple'
                    continue
                # Determino el objetivo al que le pego en caso de haber más de 1 objetivo disponible
                cambio = False
                for rect, idx in botones_obj:
                    if rect.collidepoint(e.pos):
                        juego.objetivo = idx
                        cambio = True
                        break
                if cambio:
                    continue
                # Determinamos la casilla que se tocó
                celda = celda_desde_mouse(e.pos)
                if celda:
<<<<<<< HEAD:pro.py
                    disparo_valido = juego.disparar(*celda)
                    if disparo_valido: #Disparo válido es solo consecuencia de tocado o agua, para repetidos, dibujamos todo de nuevo
                        if juego.ganador():
                            break
                # se refleja el resultado en la grilla y panel
=======
                    consumio = juego.disparar(*celda)
                    if consumio:
                        # se refleja el resultado en la grilla y panel
>>>>>>> main:Codigo/BatallaNaval.py
                        dibujar_panel(juego, botones_obj, btn_modo)
                        dibujar_grilla(juego)
                        pygame.display.flip()
                        if juego.ganador():
                            break
                        # se cambia el turno
                        juego.avanzar_turno()
                        pantalla_handoff(juego)

        # Muestra toda la pantalla principal
        pantalla.fill(FONDO)
        dibujar_panel(juego, botones_obj, btn_modo)
        dibujar_minigrilla(juego)
        dibujar_grilla(juego)
        pygame.display.flip()


if __name__ == "__main__":
    main()