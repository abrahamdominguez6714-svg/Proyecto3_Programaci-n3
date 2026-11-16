# Titulo: Menu de consola de la red de transporte (Proyecto 2)
# Autor: Abraham Dominguez Valdez
# Fecha: 16/11/2026
# Descripcion: Version por consola que usa grafo.py e io_handler.py.

from pathlib import Path

import io_handler
from grafo import Grafo, validar_peso

RUTA_CSV = Path(__file__).resolve().parent / "nodos.csv"

MENU = """
=== RED DE TRANSPORTE ===
1. Agregar conexion
2. Ver conexiones
3. Calcular ruta mas corta (Dijkstra)
4. Salir"""


def pedir_texto(mensaje: str) -> str:
    """Pide un texto no vacio."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  Error: el campo no puede estar vacio.")


def pedir_peso(mensaje: str) -> float:
    """Pide un numero finito y no negativo (minutos de viaje)."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            peso = float(texto)
            validar_peso(peso)
            return peso
        except ValueError:
            print("  Error: escribe un numero valido, mayor o igual a 0.")


def cargar_red(ruta_csv: Path) -> Grafo:
    """Lee el CSV y arma el grafo; si falla, devuelve una red vacia."""
    registros = []
    try:
        registros, avisos = io_handler.leer_conexiones(ruta_csv)
        for aviso in avisos:
            print(f"  Aviso: {aviso}")
    except FileNotFoundError:
        print("  Aviso: no existe nodos.csv; la red empieza vacia.")
    except PermissionError:
        print("  Error: no hay permiso para leer nodos.csv.")
    except (UnicodeDecodeError, OSError) as error:
        print(f"  Error al leer el archivo: {error}")
    return io_handler.construir_grafo(registros)


def opcion_agregar(ruta_csv: Path) -> None:
    """Pide una conexion y la guarda en el CSV."""
    origen = pedir_texto("Estacion origen: ")
    destino = pedir_texto("Estacion destino: ")
    if origen == destino:
        print("  Error: origen y destino deben ser distintos.")
        return
    peso = pedir_peso("Minutos de viaje: ")
    un_sentido = input("Es de un solo sentido? [s/n]: ").strip().lower()
    try:
        io_handler.guardar_conexion(
            ruta_csv, origen, destino, peso, un_sentido in {"s", "si"}
        )
    except OSError as error:
        print(f"  Error al guardar el archivo: {error}")
        return
    print("  Conexion guardada.")


def opcion_ver(grafo: Grafo) -> None:
    """Muestra las conexiones cargadas."""
    hay_conexiones = False
    for aristas in grafo.adyacencia.values():
        for arista in aristas:
            hay_conexiones = True
            print(f"  {arista}")
    if not hay_conexiones:
        print("  La red esta vacia.")


def opcion_dijkstra(grafo: Grafo) -> None:
    """Pide origen y destino y muestra la ruta mas corta."""
    if not grafo.nodos:
        print("  La red esta vacia; agrega conexiones primero.")
        return
    print("  Estaciones:", ", ".join(sorted(grafo.nodos)))
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    try:
        costo, ruta = grafo.dijkstra(origen, destino)
    except KeyError as error:
        print(f"  Error: la estacion {error.args[0]!r} no existe.")
        return
    if ruta:
        print(f"  Tiempo total: {costo:g} minutos")
        print("  Ruta:", " -> ".join(ruta))
    else:
        print(f"  No existe un camino entre {origen} y {destino}.")


def main() -> None:
    """Ciclo principal del programa."""
    grafo = cargar_red(RUTA_CSV)
    while True:
        print(MENU)
        opcion = input("Opcion: ").strip()
        if opcion == "1":
            opcion_agregar(RUTA_CSV)
            grafo = cargar_red(RUTA_CSV)
        elif opcion == "2":
            opcion_ver(grafo)
        elif opcion == "3":
            opcion_dijkstra(grafo)
        elif opcion == "4":
            print("Hasta luego.")
            return
        else:
            print("  Error: elige 1, 2, 3 o 4.")


if __name__ == "__main__":
    main()
