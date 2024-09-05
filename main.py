import flet as ft
import mariadb
import subprocess
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

    # Funcion para ir a "Acerca"
    def ir_a_acerca(e):
        # Ejecutar la pagina de "Acerca"
        page.window_close()
        subprocess.run(["python", "acerca.py"])

    # Funcion para ingresar
    def ingresar(e):
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE Email=? AND Password=?", (email_input.value, password_input.value))
            usuario = cur.fetchone()

            # Si existe un usuario
            if usuario is not None:
                # Si el usuario es el admin
                if usuario[3] == "admin@agrovision.com" and usuario[4] == "AgroVision12345":
                    # Ejecutar la pagina de un admin
                    page.window_close()
                    subprocess.run(["python", "admin.py"])
                else:
                    # Guardar la informacion del usuario en un archivo temporal
                    # Crear un 2D Array de la informacion del usuario
                    informacion_usuario = [
                        ["UsuarioID", "Nombre"],
                        [usuario[0], (str(usuario[1]) + " " + str(usuario[2]))]
                    ]
                    path = os.path.join("temp", "user.csv") # Path del archivo que se crea
                    with open(path, mode="w", newline="") as archivo:
                        writer = csv.writer(archivo)

                        for row in informacion_usuario:
                            writer.writerow(row)
                    
                    # Ejecutar la pagina de un usuario (Deteccion)
                    page.window_close()
                    subprocess.run(["python", "deteccion.py"])
            else:
                alerta_error_ingreso = ft.AlertDialog(title=ft.Text("Error en el Ingreso", size=22), content=ft.Text("Email o Password Incorrectos", size=13), on_dismiss=lambda e: print(""))
                page.open(alerta_error_ingreso)
            
            conn.close()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Header
    header = ft.Text("AgroVision", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Boton para cambiar el tema
    tema_boton = ft.ElevatedButton(text="Cambiar el Tema", icon="sunny", on_click=cambiar_tema, bgcolor="#4C956C", color="#ffffff")

    # Boton para ir a "Acerca"
    acerca_boton = ft.ElevatedButton(text="Acerca de AgroVision", icon="info", on_click=ir_a_acerca, bgcolor="#4C956C", color="#ffffff")

    # Titulo de "Ingreso"
    ingreso_titulo = ft.Text("Ingresar a AgroVision", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Campos del Formulario
    email_input = ft.TextField(label="Email", icon=ft.icons.EMAIL, hint_text="Please enter text here")
    password_input = ft.TextField(label="Password", icon=ft.icons.LOCK, hint_text="Please enter text here", password=True, can_reveal_password=True)

    # Boton para ingresar
    ingresar_boton = ft.ElevatedButton(text="Ingresar", icon=ft.icons.LOGIN, on_click=ingresar, bgcolor="#4C956C", color="#ffffff", width=700)

    # Contenedores
    # Contenedor del formulario
    global contenedor_formulario
    contenedor_formulario = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 200,
        content=ft.Column(
            controls=[
                ingreso_titulo,
                email_input,
                password_input,
                ingresar_boton
            ]
        ),
        padding=ft.padding.only(left=30, top=100)
    )

    # Contenedor del banner "Ingresar"
    contenedor_banner = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 200,
        image_src="./assets/images/Ingresar.png",
        image_fit=ft.ImageFit.FIT_HEIGHT
    )

    # Agregar los componentes a la página
    page.add(
        ft.Column(
            [
                ft.Row([header], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([tema_boton, acerca_boton], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([contenedor_formulario, contenedor_banner], alignment=ft.MainAxisAlignment.CENTER)
            ]
        )
    )

ft.app(target=main)
