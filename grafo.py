# Titulo: Grafo ponderado y algoritmo de Dijkstra (Proyectos 1 y 2)
# Autor: Abraham Dominguez Valdez
# Fecha: 16/11/2026
# Descripcion: Clases Nodo, Arista y Grafo; ruta minima con Dijkstra.

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Set, Tuple


def validar_peso(peso: float) -> None:
    """Comprueba que el peso sea un numero finito y no negativo.

    Raises:
        ValueError: si el peso es NaN, infinito o negativo.
    """
    if math.isnan(peso) or math.isinf(peso):
        raise ValueError("El peso debe ser un numero finito.")
    if peso < 0:
        raise ValueError("Dijkstra no admite pesos negativos.")


class Nodo:
    """Vertice del grafo (una estacion)."""

    def __init__(self, nombre: str) -> None:
        self.nombre: str = nombre

    def __str__(self) -> str:
        return self.nombre

    def __repr__(self) -> str:
        return f"Nodo({self.nombre!r})"


class Arista:
    """Conexion ponderada entre dos nodos (peso = minutos de viaje)."""

    def __init__(self, origen: Nodo, destino: Nodo, peso: float) -> None:
        validar_peso(peso)
        self.origen: Nodo = origen
        self.destino: Nodo = destino
        self.peso: float = peso

    def __str__(self) -> str:
        return f"{self.origen} --({self.peso:g})--> {self.destino}"


class Grafo:
    """Grafo ponderado con lista de adyacencia."""

    def __init__(self) -> None:
        self.nodos: Dict[str, Nodo] = {}
        self.adyacencia: Dict[str, List[Arista]] = {}

    def agregar_nodo(self, nombre: str) -> Nodo:
        """Agrega un nodo si no existe y lo devuelve."""
        if nombre not in self.nodos:
            self.nodos[nombre] = Nodo(nombre)
            self.adyacencia[nombre] = []
        return self.nodos[nombre]

    def agregar_arista(
        self,
        origen: str,
        destino: str,
        peso: float,
        dirigida: bool = False,
    ) -> None:
        """Conecta dos nodos; crea los nodos que falten.

        Si ``dirigida`` es False, la conexion funciona en ambos sentidos.
        El peso se valida antes de modificar el grafo.

        Raises:
            ValueError: si el peso no es valido.
        """
        validar_peso(peso)
        nodo_o = self.agregar_nodo(origen)
        nodo_d = self.agregar_nodo(destino)
        self.adyacencia[origen].append(Arista(nodo_o, nodo_d, peso))
        if not dirigida:
            self.adyacencia[destino].append(Arista(nodo_d, nodo_o, peso))

    def dijkstra(
        self, nombre_origen: str, nombre_destino: str
    ) -> Tuple[float, List[str]]:
        """Ruta mas corta entre dos nodos.

        Returns:
            (costo_total, ruta). Si no hay camino: (inf, []).

        Raises:
            KeyError: si el origen o el destino no existen en el grafo.
        """
        for nombre in (nombre_origen, nombre_destino):
            if nombre not in self.nodos:
                raise KeyError(nombre)

        distancias: Dict[str, float] = {n: math.inf for n in self.nodos}
        distancias[nombre_origen] = 0.0
        anterior: Dict[str, Optional[str]] = {n: None for n in self.nodos}
        visitados: Set[str] = set()
        cola: List[Tuple[float, str]] = [(0.0, nombre_origen)]

        while cola:
            distancia_actual, actual = heapq.heappop(cola)
            if actual in visitados:
                continue
            visitados.add(actual)
            if actual == nombre_destino:
                break
            for arista in self.adyacencia[actual]:
                vecino = arista.destino.nombre
                if vecino in visitados:
                    continue
                nueva = distancia_actual + arista.peso
                if nueva < distancias[vecino]:
                    distancias[vecino] = nueva
                    anterior[vecino] = actual
                    heapq.heappush(cola, (nueva, vecino))

        if math.isinf(distancias[nombre_destino]):
            return math.inf, []

        # Se reconstruye la ruta hacia atras con los nodos anteriores
        ruta: List[str] = []
        nodo: Optional[str] = nombre_destino
        while nodo is not None:
            ruta.append(nodo)
            nodo = anterior[nodo]
        ruta.reverse()
        return distancias[nombre_destino], ruta
