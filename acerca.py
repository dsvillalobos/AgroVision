import flet as ft
import subprocess
import webbrowser

def main(page: ft.page):
    page.title = "AgroVision"
    page.window_width = 1300
    page.window_height = 700
    page.scroll = "adaptive"  # Permitir scroll en la ventana
    page.theme_mode = "light"  # Escoger el tema (system, dark, light)

    # Funcion para cambiar el tema
    def cambiar_tema(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        page.update()

    # Funcion para regresar
    def regresar(e):
        # Ejecutar la pagina main (pagina principal o de inicio)
        page.window_close()
        subprocess.run(["python", "main.py"])

    # Funcion para abrir la documentacion
    def abrir_documentacion(e):
        webbrowser.open("https://drive.google.com/file/d/1_kKfcIY7_TYXMrK6JALTNj94atUlDyXB/view?usp=drive_link")

    # Funcion para abir la documentacion del administrador
    def abrir_documentacion_admin(e):
        webbrowser.open("https://drive.google.com/file/d/1C9DD-zeh7qVqySL18rwG0dUV9ZAWxor9/view?usp=drive_link")

    # Funcion para abir la documentacion del usuario
    def abrir_documentacion_usuario(e):
        webbrowser.open("https://drive.google.com/file/d/1nWLr6M7lDupep4VI0041nGWkhmH76ncE/view?usp=sharing")

    # Header
    header = ft.Text("AgroVision", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Boton para cambiar el tema
    tema_boton = ft.ElevatedButton(text="Cambiar el Tema", icon="sunny", on_click=cambiar_tema, bgcolor="#4C956C", color="#ffffff")

    # Boton para regresar
    regresar_boton = ft.ElevatedButton(text="Regresar al Ingreso", icon="arrow_back", on_click=regresar, bgcolor="#4C956C", color="#ffffff")

    # Titulo del "Centro de Ayuda"
    centro_ayuda_titulo = ft.Text("Centro de Ayuda", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Boton para la documentacion
    documentacion_boton = ft.ElevatedButton(text="Documentación de AgroVision", icon="book", on_click=abrir_documentacion, bgcolor="#4C956C", color="#ffffff", width=700)

    # Boton para la documentacion del administrador
    documentacion_administrador_boton = ft.ElevatedButton(text="Manual del Administrador", icon="admin_panel_settings", on_click=abrir_documentacion_admin, bgcolor="#4C956C", color="#ffffff", width=700)

    # Boton para la documentacion del usuario
    documentacion_usuario_boton = ft.ElevatedButton(text="Manual del Usuario", icon="person_sharp", on_click=abrir_documentacion_usuario, bgcolor="#4C956C", color="#ffffff", width=700)

    # Contenedores
    # Contenedor del banner "Acerca"
    global contenedor_banner
    contenedor_banner = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 200,
        image_src="./assets/images/Acerca.png",
        image_fit=ft.ImageFit.FIT_HEIGHT
    )

    # Contenedor del centro de ayuda
    global contenedor_ayuda
    contenedor_ayuda = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 200,
        content=ft.Column([
            centro_ayuda_titulo,
            documentacion_boton,
            documentacion_administrador_boton,
            documentacion_usuario_boton
        ])
    )


    # Agregar los componentes a la página
    page.add(
        ft.Column(
            [
                ft.Row([header], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([tema_boton, regresar_boton], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([contenedor_banner, contenedor_ayuda], alignment=ft.MainAxisAlignment.CENTER)
            ]
        )
    )

ft.app(target=main)
