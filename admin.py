import flet as ft
import mariadb
import base64
import subprocess
import matplotlib.pyplot as plt
from io import BytesIO
import csv
import os

def main(page: ft.Page):
    page.title = "AgroVision"
    page.window_width = 1300
    page.window_height = 700
    page.scroll = "adaptive"  # Permitir scroll en la ventana
    page.theme_mode = "light"  # Escoger el tema (system, dark, light)

    # Funcion para cambiar el tema
    def cambiar_tema(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    # Funcion para exportar las detecciones
    def exportar_detecciones(e):
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("SELECT * FROM vista_detecciones")
            detecciones = cur.fetchall()
            conn.close()

            path = os.path.join("exports", "data.csv") # Path del archivo que se crea
            with open(path, mode="w", newline="") as archivo:
                campos = ["DeteccionID", "Carrots", "Eggplants", "Potatoes", "Tomatoes", "Fecha", "Hora", "UsuarioID", "Nombre", "Apellido"]
                writer = csv.DictWriter(archivo, fieldnames=campos)
                writer.writeheader()
                
                for deteccion in detecciones:
                    deteccion_dicccionario = {campos[i]: deteccion[i] for i in range(len(campos))}
                    writer.writerow(deteccion_dicccionario)

            alerta_exito_exportado = ft.AlertDialog(title=ft.Text("Éxito", size=22), content=ft.Text("Las detecciones se han exportado correctamente.", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_exito_exportado)
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Funcion para cerrar sesion
    def cerrar_sesion(e):
        # Ejecutar la pagina main (pagina principal o de inicio)
        page.window_close()
        subprocess.run(["python", "main.py"])

    # Funcion para agregar el usuario
    def agregar_usuario(e):
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("INSERT INTO usuarios (Nombre, Apellido, Email, Password) VALUES (?, ?, ?, ?)", (nombre_input.value, apellido_input.value, email_input.value, password_input.value))
            conn.commit()
            alerta_exito_guardado = ft.AlertDialog(title=ft.Text("Éxito", size=22), content=ft.Text("El usuario se ha agregado correctamente.", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_exito_guardado)
            conn.close()
            actualizar_tabla()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Funcion para actualizar la tabla
    def actualizar_tabla():
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios")
            usuarios = cur.fetchall()
            conn.close()
            usuarios_tabla.rows.clear()

            for usuario in usuarios:
                usuarios_tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(usuario[1])),
                        ft.DataCell(ft.Text(usuario[2])),
                        ft.DataCell(ft.Text(usuario[3])),
                    ])
                )

            page.update()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Funcion para actualizar el grafico de detecciones
    def actualizar_grafico():
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("SELECT * FROM vista_detecciones")
            detecciones = cur.fetchall()
            conn.close()

            # Variables para las detecciones de hortalizas
            zanahoria = sum([d[1] for d in detecciones])
            berenjena = sum([d[2] for d in detecciones])
            patata = sum([d[3] for d in detecciones])
            tomate = sum([d[4] for d in detecciones])

            # Filtrar los datos para excluir las hortalizas con valor 0
            grafico_labels = ["Zanahoria", "Berenjena", "Patata", "Tomate"]
            grafico_data = [zanahoria, berenjena, patata, tomate]
            grafico_colors = ["#ee6c4d", "#6d597a", "#f9c74f", "#e56b6f"]

            # Filtrar los datos para excluir las hortalizas con valor 0
            filtered_labels = [label for label, data in zip(grafico_labels, grafico_data) if data > 0]
            filtered_data = [data for data in grafico_data if data > 0]
            filtered_colors = [color for color, data in zip(grafico_colors, grafico_data) if data > 0]

            # Verifica que hay datos después de filtrar para mostrar un gráfico
            if filtered_data:
                fig, ax = plt.subplots()
                ax.pie(filtered_data, labels=filtered_labels, colors=filtered_colors, autopct='%1.0f%%')
                ax.axis("equal")
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                grafico_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                buf.close()
                grafico_detecciones.src_base64 = grafico_base64

                page.update()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Funcion para actualizar la tabla de las detecciones
    def actualizar_tabla_detecciones():
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("SELECT * FROM vista_detecciones")
            detecciones = cur.fetchall()
            conn.close()
            detecciones_tabla.rows.clear()

            for deteccion in detecciones:
                detecciones_tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(deteccion[0])),
                        ft.DataCell(ft.Text(deteccion[1])),
                        ft.DataCell(ft.Text(deteccion[2])),
                        ft.DataCell(ft.Text(deteccion[3])),
                        ft.DataCell(ft.Text(deteccion[4])),
                        ft.DataCell(ft.Text(deteccion[5])),
                        ft.DataCell(ft.Text(deteccion[6])),
                        ft.DataCell(ft.Text(value=f"{deteccion[8]} {deteccion[9]}")),
                    ])
                )

            page.update()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Header
    header = ft.Text("AgroVision", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Boton para cambiar el tema
    tema_boton = ft.ElevatedButton(text="Cambiar el Tema", icon="sunny", on_click=cambiar_tema, bgcolor="#4C956C", color="#ffffff")

    # Boton para exportar las detecciones como csv
    exportar_boton = ft.ElevatedButton(text="Exportar Detecciones en Formato .CSV", icon="file_copy", on_click=exportar_detecciones, bgcolor="#4C956C", color="#ffffff")

    # Boton para cerrar sesion
    cerrar_sesion_boton = ft.ElevatedButton(text="Cerrar Sesión", icon="logout", on_click=cerrar_sesion, bgcolor="#4C956C", color="#ffffff")

    # Titulo del "Agregar Usuario"
    agregar_usuario_titulo = ft.Text("Agregar Usuario (Agricultor)", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Titulo para la grafica de detecciones
    grafico_detecciones_titulo = ft.Text("Gráfico de Pastel de las Detecciones", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Titulo para la tabla de detecciones
    detecciones_tabla_titulo = ft.Text("Todas las Detecciones", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Campos del formulario
    nombre_input = ft.TextField(label="Nombre", icon=ft.icons.PERSON_SHARP, hint_text="Please enter text here")
    apellido_input = ft.TextField(label="Apellido", icon=ft.icons.PERSON_SHARP, hint_text="Please enter text here")
    email_input = ft.TextField(label="Email", icon=ft.icons.EMAIL, hint_text="Please enter text here")
    password_input = ft.TextField(label="Password", icon=ft.icons.LOCK, hint_text="Please enter text here", password=True, can_reveal_password=True)

    # Boton para agregar el usuario
    agregar_usuario_boton = ft.ElevatedButton(text="Agregar", icon=ft.icons.ADD, on_click=agregar_usuario, bgcolor="#4C956C", color="#ffffff", width=700)

    # Tabla de los usuarios
    global usuarios_tabla
    usuarios_tabla = ft.DataTable(
        heading_row_color=ft.colors.BLACK12,
        width=700,
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Email")),
        ],
        rows=[]
    )

    # Grafico de barra con las detecciones
    global grafico_detecciones
    grafico_detecciones = ft.Image()

    # Tabla de las detecciones
    global detecciones_tabla
    detecciones_tabla = ft.DataTable(
        heading_row_color=ft.colors.BLACK12,
        width=page.window_width,
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Zanahorias")),
            ft.DataColumn(ft.Text("Berenjenas")),
            ft.DataColumn(ft.Text("Patatas")),
            ft.DataColumn(ft.Text("Tomates")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Hora")),
            ft.DataColumn(ft.Text("Realizada por")),
        ],
        rows=[]
    )

    # Contenedores
    # Contenedor del formulario para agregar un usuario
    global contenedor_form
    contenedor_form = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 125,
        content=ft.Column(
            controls=[
                agregar_usuario_titulo,
                nombre_input,
                apellido_input,
                email_input,
                password_input,
                agregar_usuario_boton,
                usuarios_tabla
            ]
        )
    )

    # Contenedor del dashboard de las detecciones
    global contenedor_detecciones
    contenedor_detecciones = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 125,
        content=ft.Column(
            controls=[
                grafico_detecciones_titulo,
                grafico_detecciones
            ]
        )
    )

    # Contenedor con la tabla de todas las detecciones
    global contenedor_tabla_detecciones
    contenedor_tabla_detecciones = ft.Container(
        width=page.window_width * 1,  # El 100% de la ventana
        height=page.window_height - 125,
        content=ft.Column(
            controls=[
                detecciones_tabla_titulo,
                detecciones_tabla
            ]
        )
    )

    # Agregar los componentes a la página
    page.add(
        ft.Column(
            [
                ft.Row([header], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([tema_boton, exportar_boton,cerrar_sesion_boton], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([contenedor_form, contenedor_detecciones], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([contenedor_tabla_detecciones], alignment=ft.MainAxisAlignment.CENTER)
            ]
        )
    )

    actualizar_tabla()
    actualizar_grafico()
    actualizar_tabla_detecciones()

ft.app(target=main)