# Titulo: Interfaz web de la red de transporte con Dijkstra (Streamlit)
# Autor: Abraham Dominguez Valdez
# Fecha: 16/11/2026
# Descripcion: Frontend en Streamlit sobre grafo.py e io_handler.py.

from pathlib import Path

import pandas as pd
import streamlit as st

import io_handler
from grafo import validar_peso

RUTA_CSV = Path(__file__).resolve().parent / "nodos.csv"
COLUMNAS_CONEXIONES = ["Origen", "Destino", "Minutos", "Sentido"]


def inicializar_estado() -> None:
    """Lee nodos.csv una sola vez por sesion y guarda el grafo en RAM."""
    if "grafo" in st.session_state:
        return
    registros = []
    avisos = []
    try:
        registros, avisos = io_handler.leer_conexiones(RUTA_CSV)
    except FileNotFoundError:
        avisos.append("No se encontró nodos.csv; la red empieza vacía.")
    except PermissionError:
        avisos.append("No hay permiso para leer nodos.csv.")
    except (UnicodeDecodeError, OSError) as error:
        avisos.append(f"No se pudo leer nodos.csv: {error}")
    st.session_state["conexiones"] = registros
    st.session_state["grafo"] = io_handler.construir_grafo(registros)
    st.session_state["avisos"] = avisos


def registrar_conexion(origen, destino, texto_peso, un_sentido) -> None:
    """Valida los datos, los guarda en nodos.csv y actualiza el grafo."""
    origen = origen.strip()
    destino = destino.strip()
    if not origen or not destino:
        st.warning("Escribe el nombre de las dos estaciones.")
        return
    if origen == destino:
        st.warning("El origen y el destino deben ser distintos.")
        return

    try:
        peso = float(texto_peso.strip().replace(",", "."))
    except ValueError:
        st.error("El peso debe ser un número (por ejemplo 5 o 3.5).")
        return
    try:
        validar_peso(peso)
    except ValueError as error:
        st.error(str(error))
        return

    # Primero al disco; si falla, la memoria no se modifica
    try:
        io_handler.guardar_conexion(
            RUTA_CSV, origen, destino, peso, un_sentido
        )
    except PermissionError:
        st.error("No hay permiso para escribir en nodos.csv.")
        return
    except OSError as error:
        st.error(f"No se pudo guardar nodos.csv: {error}")
        return

    # Después al grafo que vive en st.session_state (sin releer el CSV)
    st.session_state["grafo"].agregar_arista(
        origen, destino, peso, un_sentido
    )
    st.session_state["conexiones"].append((origen, destino, peso, un_sentido))
    st.success(f"Conexión guardada: {origen} → {destino} ({peso:g} min).")


def calcular_ruta(origen, destino) -> None:
    """Ejecuta Dijkstra y muestra el costo total y el recorrido."""
    origen = origen.strip()
    destino = destino.strip()
    if not origen or not destino:
        st.warning("Escribe el nodo origen y el nodo destino.")
        return
    try:
        costo, ruta = st.session_state["grafo"].dijkstra(origen, destino)
    except KeyError as error:
        st.error(f"La estación '{error.args[0]}' no existe en la red.")
        return
    if not ruta:
        st.warning(f"No existe una ruta posible entre {origen} y {destino}.")
        return

    col_costo, col_tramos = st.columns(2)
    with col_costo:
        st.metric("Costo total mínimo", f"{costo:g} min")
    with col_tramos:
        st.metric("Tramos del recorrido", len(ruta) - 1)
    st.success("Recorrido: " + " → ".join(ruta))


def tabla_conexiones() -> pd.DataFrame:
    """Arma el DataFrame con las conexiones registradas."""
    filas = []
    for origen, destino, peso, dirigida in st.session_state["conexiones"]:
        filas.append(
            {
                "Origen": origen,
                "Destino": destino,
                "Minutos": peso,
                "Sentido": "Un sentido" if dirigida else "Dos sentidos",
            }
        )
    return pd.DataFrame(filas, columns=COLUMNAS_CONEXIONES)


def tabla_estaciones() -> pd.DataFrame:
    """Arma el DataFrame con el catálogo de estaciones."""
    adyacencia = st.session_state["grafo"].adyacencia
    filas = [
        {"Estación": nombre, "Conexiones salientes": len(aristas)}
        for nombre, aristas in sorted(adyacencia.items())
    ]
    return pd.DataFrame(filas, columns=["Estación", "Conexiones salientes"])


def mostrar_visor() -> None:
    """Pestaña con la red actual en tablas."""
    st.header("Red actual")
    for aviso in st.session_state["avisos"]:
        st.warning(aviso)

    conexiones = tabla_conexiones()
    if conexiones.empty:
        st.info("La red está vacía. Agrega conexiones en la pestaña Registro.")
        return
    st.subheader("Conexiones")
    st.dataframe(conexiones, use_container_width=True)
    with st.expander("Catálogo de estaciones"):
        st.dataframe(tabla_estaciones(), use_container_width=True)


def mostrar_registro() -> None:
    """Pestaña para registrar nuevas conexiones."""
    st.header("Registrar una conexión")
    with st.form("form_conexion"):
        col_origen, col_destino = st.columns(2)
        with col_origen:
            origen = st.text_input("Estación origen")
        with col_destino:
            destino = st.text_input("Estación destino")
        texto_peso = st.text_input("Minutos de viaje", value="5")
        un_sentido = st.checkbox("Es de un solo sentido")
        enviado = st.form_submit_button("Guardar conexión")
    if enviado:
        registrar_conexion(origen, destino, texto_peso, un_sentido)


def mostrar_calculador() -> None:
    """Pestaña para calcular la ruta más corta."""
    st.header("Ruta más corta (Dijkstra)")
    with st.form("form_ruta"):
        col_origen, col_destino = st.columns(2)
        with col_origen:
            origen = st.text_input("Nodo origen")
        with col_destino:
            destino = st.text_input("Nodo destino")
        enviado = st.form_submit_button("Calcular ruta")
    if enviado:
        calcular_ruta(origen, destino)
    with st.expander("Estaciones disponibles"):
        nombres = sorted(st.session_state["grafo"].nodos)
        st.write(", ".join(nombres) if nombres else "Aún no hay estaciones.")


def mostrar_barra_lateral() -> None:
    """Barra lateral con datos generales de la red."""
    st.sidebar.title("Red de transporte")
    st.sidebar.caption("Programación III · Proyecto 3")
    st.sidebar.metric("Estaciones", len(st.session_state["grafo"].nodos))
    st.sidebar.metric("Conexiones", len(st.session_state["conexiones"]))


def main() -> None:
    """Arma la página completa."""
    st.set_page_config(page_title="Red de transporte", page_icon="🚇")
    inicializar_estado()
    st.title("Red de transporte con Dijkstra")

    tab_visor, tab_registro, tab_ruta = st.tabs(
        ["Visor de red", "Registro", "Calculador"]
    )
    # Se procesa primero el registro para que las demás pestañas
    # ya vean los datos nuevos
    with tab_registro:
        mostrar_registro()
    with tab_visor:
        mostrar_visor()
    with tab_ruta:
        mostrar_calculador()
    mostrar_barra_lateral()


main()
