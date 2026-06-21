import random
import time

FILAS = COLUMNAS = 10
FLOTA = [4, 3, 2, 2]
BOMBAS_CRUZ = 3


class Tablero:
    def __init__(self):
        self.barcos = [[0] * COLUMNAS for i in range(FILAS)]
        self.disparos = [[None] * COLUMNAS for j in range(FILAS)]
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
    def __init__(self, numero):
        self.numero = numero
        self.nombre = f"Jugador {numero}"
        self.tablero = Tablero()
        self.bombas = BOMBAS_CRUZ
        self.vivo = True


class Juego:
    def __init__(self, cantidad):
        self.jugadores = [Jugador(i + 1) for i in range(cantidad)]
        self.turno = 0
        self.modo = 'simple'
        self.objetivo = None
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


__all__ = ['Jugador', 'Juego', 'FILAS', 'COLUMNAS']
