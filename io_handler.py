# Titulo: Lectura y escritura de la red en CSV (persistencia)
# Autor: Abraham Dominguez Valdez
# Fecha: 16/11/2026
# Descripcion: Lee y guarda conexiones en nodos.csv y arma el Grafo.

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import List, Tuple

from grafo import Grafo

ENCABEZADO: List[str] = ["origen", "destino", "peso", "dirigida"]
Registro = Tuple[str, str, float, bool]


def _a_bool(texto: str) -> bool:
    """Convierte un texto del CSV (1, si, true...) en booleano."""
    return texto.strip().lower() in {"1", "true", "si", "s", "yes"}


def guardar_conexion(
    ruta_csv: Path, origen: str, destino: str, peso: float, dirigida: bool
) -> None:
    """Agrega una conexion al CSV (crea archivo y encabezado si faltan).

    Raises:
        PermissionError: si no hay permiso para escribir.
        OSError: si el archivo no se puede escribir.
    """
    nuevo = not ruta_csv.exists() or ruta_csv.stat().st_size == 0
    with ruta_csv.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        if nuevo:
            escritor.writerow(ENCABEZADO)
        escritor.writerow([origen, destino, f"{peso:g}", int(dirigida)])


def leer_conexiones(ruta_csv: Path) -> Tuple[List[Registro], List[str]]:
    """Lee el CSV y devuelve (registros_validos, advertencias).

    Las filas danadas no detienen la carga: se omiten y se reportan.

    Raises:
        FileNotFoundError: si el archivo no existe.
        PermissionError: si no hay permiso para leerlo.
        UnicodeDecodeError: si el archivo no es texto UTF-8.
    """
    registros: List[Registro] = []
    avisos: List[str] = []
    with ruta_csv.open("r", newline="", encoding="utf-8") as archivo:
        for num, fila in enumerate(csv.reader(archivo), start=1):
            if not fila or (num == 1 and fila[0].strip().lower() == "origen"):
                continue
            if len(fila) < 3:
                avisos.append(f"Linea {num}: faltan columnas, se omite.")
                continue
            origen, destino = fila[0].strip(), fila[1].strip()
            try:
                peso = float(fila[2])
            except ValueError:
                avisos.append(f"Linea {num}: peso invalido {fila[2]!r}.")
                continue
            if not origen or not destino:
                avisos.append(f"Linea {num}: nombre de nodo vacio.")
                continue
            if math.isnan(peso) or math.isinf(peso) or peso < 0:
                avisos.append(f"Linea {num}: peso fuera de rango ({peso}).")
                continue
            dirigida = _a_bool(fila[3]) if len(fila) > 3 else False
            registros.append((origen, destino, peso, dirigida))
    return registros, avisos


def construir_grafo(registros: List[Registro]) -> Grafo:
    """Arma un Grafo en memoria a partir de los registros leidos."""
    grafo = Grafo()
    for origen, destino, peso, dirigida in registros:
        grafo.agregar_arista(origen, destino, peso, dirigida)
    return grafo
