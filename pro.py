import tkinter as tk
import pygame
import sys

from game_logic import Juego, FILAS, COLUMNAS

# =====================================================================
# CONFIGURACION GENERAL
# =====================================================================
TAM_CELDA = 38
MARGEN = 2

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

    texto("Atacar a:", 20, 185, fuente)
    for rect, idx in botones_obj:
        sel = (idx == juego.objetivo)
        pygame.draw.rect(pantalla, BTN_SEL if sel else BTN, rect)
        texto(juego.jugadores[idx].nombre, rect.centerx, rect.centery,
              fuente_p, BLANCO, centrado=True)

    texto(juego.mensaje, 20, ALTO - 60, fuente_p, AMARILLO)


def construir_botones(juego):
    botones_obj = [] # HACen referencia al jugador al que le vas a pregar
    y = 215
    for j in juego.oponentes():
        idx = juego.jugadores.index(j)
        botones_obj.append((pygame.Rect(20, y, 200, 36), idx))
        y += 44
    btn_modo = pygame.Rect(20, 100, 200, 36)
    return botones_obj, btn_modo


def celda_desde_mouse(pos):
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

# Arranca el juego
def main():
    cantidad = pantalla_config()
    juego = Juego(cantidad) #Cantidad es cantidad de jugadores, nada de muchos juegos eh
    pantalla_handoff(juego)

    while True:
        ganador = juego.ganador() # Devuelve el array de jugadores que están vivos, si hay uno solo, es el ganador
        if ganador:
            pantalla_fin(ganador)

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
                    disparo_valido = juego.disparar(*celda)
                    if disparo_valido: #Disparo válido es solo consecuencia de tocado o agua, para repetidos, dibujamos todo de nuevo
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