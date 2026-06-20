import tkinter as tk
import time
import pygame
import sys
import random

# =====================================================================
# CONFIGURACION GENERAL
# =====================================================================
FILAS = COLUMNAS = 10
TAM_CELDA = 38
MARGEN = 2
FLOTA = [4, 3, 2, 2]      # tamaños de los barcos de cada jugador
BOMBAS_CRUZ = 3           # bombas en cruz disponibles por jugador

ANCHO = 900
ALTO = 660
GRID_X = 320             # esquina superior izquierda de la grilla objetivo
GRID_Y = 150

# Colores
FONDO        = (18, 32, 47)
PANEL        = (27, 47, 66)
DESCONOCIDO  = (41, 128, 185)   # celda no disparada (niebla)
AGUA         = (149, 165, 166)  
TOCADO       = (231, 76, 60)  
BLANCO       = (236, 240, 241)
GRIS         = (127, 140, 141)
VERDE        = (46, 204, 113)
AMARILLO     = (241, 196, 15)
BTN          = (52, 73, 94)
BTN_SEL      = (41, 128, 185)


# =====================================================================
# MODELO: TABLERO Y JUGADOR
# =====================================================================
class Tablero:
    def _init_(self):
        self.barcos = [[0] * COLUMNAS for i in range(FILAS)]      # 1 = hay barco
        self.disparos = [[None] * COLUMNAS for j in range(FILAS)] # None / 'agua' / 'tocado'
        self.celdas_barco = 0
        self._colocar_flota()

    def _colocar_flota(self):
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

    def recibir_disparo(self, f, c):
        """Devuelve 'agua', 'tocado' o 'repetido'."""
        if self.disparos[f][c] is not None:
            return 'repetido'
        if self.barcos[f][c] == 1:
            self.disparos[f][c] = 'tocado'
            self.celdas_barco -= 1
            return 'tocado'
        self.disparos[f][c] = 'agua'
        return 'agua'

    @property
    def hundido(self):
        return self.celdas_barco <= 0


class Jugador:
    def _init_(self, numero):
        self.numero = numero
        self.nombre = f"Jugador {numero}"
        self.tablero = Tablero()
        self.bombas = BOMBAS_CRUZ
        self.vivo = True


# =====================================================================
# LOGICA DE PARTIDA
# =====================================================================
class Juego:
    def _init_(self, cantidad):
        self.jugadores = [Jugador(i + 1) for i in range(cantidad)]
        self.turno = 0                  # indice del jugador actual
        self.modo = 'simple'            # 'simple' o 'bomba'
        self.objetivo = None            # indice del jugador objetivo
        self.mensaje = ""
        self._elegir_objetivo_inicial()

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
            self.mensaje += f"  {objetivo.nombre} fue eliminado."
        return True

    def avanzar_turno(self):
        time.sleep(1)
        for _ in range(len(self.jugadores)):
            self.turno = (self.turno + 1) % len(self.jugadores)
            if self.actual.vivo:
                break
        self.modo = 'simple'
        self.mensaje = ""
        self._elegir_objetivo_inicial()

    def ganador(self):
        v = self.vivos()
        return v[0] if len(v) == 1 else None


# =====================================================================
# DIBUJO
# =====================================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Batalla Naval Multijugador")
fuente   = pygame.font.SysFont("Arial", 20)
fuente_b = pygame.font.SysFont("Arial", 26, bold=True)
fuente_p = pygame.font.SysFont("Arial", 16)


def texto(txt, x, y, f=fuente, color=BLANCO, centrado=False):
    img = f.render(txt, True, color)
    rect = img.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    pantalla.blit(img, rect)


def dibujar_grilla(juego):
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
                color = DESCONOCIDO
            x = GRID_X + c * (TAM_CELDA + MARGEN)
            y = GRID_Y + f * (TAM_CELDA + MARGEN)
            pygame.draw.rect(pantalla, color, (x, y, TAM_CELDA, TAM_CELDA))


def dibujar_panel(juego, botones_obj, btn_modo):
    pygame.draw.rect(pantalla, PANEL, (0, 0, 300, ALTO))
    texto(juego.actual.nombre, 20, 25, fuente_b, VERDE)
    texto(f"Bombas en cruz: {juego.actual.bombas}", 20, 70, fuente_p)

    modo_txt = "BOMBA EN CRUZ" if juego.modo == 'bomba' else "DISPARO SIMPLE"
    pygame.draw.rect(pantalla, BTN_SEL if juego.modo == 'bomba' else BTN, btn_modo)
    texto(modo_txt, btn_modo.centerx, btn_modo.centery, fuente_p, BLANCO, centrado=True)
    texto("(B = cambiar modo)", 20, 145, fuente_p, GRIS)

    texto("Atacar a:", 20, 185, fuente)
    for rect, idx in botones_obj:
        sel = (idx == juego.objetivo)
        pygame.draw.rect(pantalla, BTN_SEL if sel else BTN, rect)
        texto(juego.jugadores[idx].nombre, rect.centerx, rect.centery,
              fuente_p, BLANCO, centrado=True)

    texto(juego.mensaje, 20, ALTO - 60, fuente_p, AMARILLO)


def construir_botones(juego):
    botones_obj = []
    y = 215
    for j in juego.oponentes():
        idx = juego.jugadores.index(j)
        botones_obj.append((pygame.Rect(20, y, 200, 36), idx))
        y += 44
    btn_modo = pygame.Rect(20, 100, 200, 36)
    return botones_obj, btn_modo


def celda_desde_mouse(pos):
    mx, my = pos
    c = (mx - GRID_X) // (TAM_CELDA + MARGEN)
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
        texto("BATALLA NAVAL", ANCHO // 2, 120, fuente_b, BLANCO, centrado=True)
        texto("¿Cuantos jugadores?", ANCHO // 2, 200, fuente, BLANCO, centrado=True)
        texto(str(cantidad), ANCHO // 2, 270, fuente_b, AMARILLO, centrado=True)
        texto("← / →  para cambiar   |   ENTER para empezar",
              ANCHO // 2, 360, fuente_p, GRIS, centrado=True)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT:
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
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()


# =====================================================================
# BUCLE PRINCIPAL
# =====================================================================
def main():
    cantidad = pantalla_config()
    juego = Juego(cantidad)
    pantalla_handoff(juego)

    while True:
        ganador = juego.ganador()
        if ganador:
            pantalla_fin(ganador)

        botones_obj, btn_modo = construir_botones(juego)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_b:
                if juego.actual.bombas > 0:
                    juego.modo = 'bomba' if juego.modo == 'simple' else 'simple'

            if e.type == pygame.MOUSEBUTTONDOWN:
                # ¿clic en boton de modo?
                if btn_modo.collidepoint(e.pos) and juego.actual.bombas > 0:
                    juego.modo = 'bomba' if juego.modo == 'simple' else 'simple'
                    continue
                # ¿clic en un objetivo?
                cambio = False
                for rect, idx in botones_obj:
                    if rect.collidepoint(e.pos):
                        juego.objetivo = idx
                        cambio = True
                        break
                if cambio:
                    continue
                # ¿clic en la grilla?
                celda = celda_desde_mouse(e.pos)
                if celda:
                    consumio = juego.disparar(*celda)
                    if consumio:
                        if juego.ganador():
                            break
                # se refleja el resultado en la grilla y panel
                        dibujar_panel(juego, botones_obj, btn_modo)
                        dibujar_grilla(juego)
                        pygame.display.flip()
                # se cambia el turno
                        juego.avanzar_turno()
                        pantalla_handoff(juego)

        pantalla.fill(FONDO)
        dibujar_panel(juego, botones_obj, btn_modo)
        dibujar_grilla(juego)
        pygame.display.flip()


if __name__ == "__main__":
    main()