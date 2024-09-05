import flet as ft
import cv2
import base64
from ultralytics import YOLO
import mariadb
import subprocess
import matplotlib.pyplot as plt
from io import BytesIO
import csv
import os

# Inicializar el modelo de detección
model = YOLO(r"models/best.pt")

# Variables para las detecciones de hortalizas
zanahoria = 0
berenjena = 0
patata = 0
tomate = 0

# Obtener la informacion del usuario que acaba de ingresar
informacion_usuario = []
path = os.path.join("temp", "user.csv") # Path del archivo que se crea
with open(path, mode="r", newline="") as archivo:
    reader = csv.reader(archivo)
    
    for row in reader:
        informacion_usuario.append(row)

# Clase para procesar y mostrar la imagen con detección de objetos
class ProcesadaImagen(ft.UserControl):
    def __init__(self, image_path, update_table):
        super().__init__()
        self.image_path = image_path
        self.detections_count = {}
        self.update_table = update_table

    def did_mount(self):
        self.process_image()

    def process_image(self):
        global zanahoria, berenjena, patata, tomate  # Accede a las variables globales

        # Leer la imagen desde el archivo proporcionado
        frame = cv2.imread(self.image_path)
        # Realiza la detección de objetos en el frame utilizando el modelo YOLO
        results = model.predict(frame, imgsz=640, conf=0.10) # Se le establece un nivel de confianza del 0.10 es decir, el 10%

        if len(results) != 0:
            # Inicializa el diccionario para contar las detecciones por clase
            self.detections_count = {}

            for box in results[0].boxes:
                class_name = box.cls[0].item()  # Obtiene la clase de la detección
                class_name_str = model.names[class_name]  # Obtiene el nombre de la clase

                if class_name_str in self.detections_count:
                    self.detections_count[class_name_str] += 1
                else:
                    self.detections_count[class_name_str] = 1

            # Selecciona la detección con mayor confianza
            best_result = max(results[0].boxes, key=lambda box: box.conf)

            # Anota el resultado en el frame
            annotated_frame = results[0].plot(boxes=[best_result])

            # Codifica el frame anotado en formato PNG
            _, im_arr = cv2.imencode(".png", annotated_frame)
            # Codifica la imagen en base64 para poder mostrarla en la interfaz gráfica
            im_b64 = base64.b64encode(im_arr).decode("utf-8")
            # Actualiza la fuente de la imagen en la UI
            self.img.src_base64 = im_b64
            self.update()

        # Actualiza las variables globales según las detecciones
        for cls, count in self.detections_count.items():
            if cls == "zanahoria":
                zanahoria += count

            if cls == "berenjena":
                berenjena += count

            if cls == "patata":
                patata += count
                
            if cls == "tomate":
                tomate += count

        # Actualiza la tabla de dashboard
        self.update_table()

    def build(self):
        # Crea un objeto Image de Flet para mostrar la imagen procesada en la UI
        self.img = ft.Image(
            border_radius=ft.border_radius.all(20),
            width=640,
            height=480
        )
        return self.img

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

    # Funcion para cerrar sesion
    def cerrar_sesion(e):
        # Ejecutar la pagina main (pagina principal o de inicio)
        page.window_close()
        subprocess.run(["python", "main.py"])

    # Funcion para seleccionar el archivo y mostrar la imagen procesada
    def seleccionar_archivo(e):
        if e.files:
            imagen_path = e.files[0].path
            contenedor_deteccion.content = ProcesadaImagen(imagen_path, actualizar_tabla)
            page.update()

    # Funcion para reiniciar la ventana de la deteccion
    def reiniciar_deteccion(e):
        page.window_close()
        subprocess.run(["python", "deteccion.py"])

    # Guardar resultados en la base de datos
    def guardar_resultados(e):
        try:
            conn = mariadb.connect(
                user="root",
                password="",
                host="localhost",
                port=3306,
                database="agrovision"
            )

            cur = conn.cursor()
            cur.execute("INSERT INTO detecciones (Carrots, Eggplants, Potatoes, Tomatoes, UsuarioID) VALUES (?, ?, ?, ?, ?)", (zanahoria, berenjena, patata, tomate, informacion_usuario[1][0]))
            conn.commit()
            alerta_exito_guardado = ft.AlertDialog(title=ft.Text("Éxito", size=22), content=ft.Text("Se han guardado correctamente las estadísticas sobre la detección.\n\nPor ende, se reiniciarán las estadísticas, pues se da por concluida la sesión.", size=13), actions=[
                ft.ElevatedButton("Aceptar", on_click=reiniciar_deteccion)
            ], on_dismiss=lambda e: print(""))
            page.open(alerta_exito_guardado)
            
            conn.close()
        except mariadb.Error as err:
            # Capturando una Excepcion
            alerta_excepcion = ft.AlertDialog(title=ft.Text("Error de Conexion", size=22), content=ft.Text("Revisa que estes conectado a\nHost: localhost\nPuerto: 3306\nUser: root\nPassword:\nBase de Datos: agrovision", size=13), on_dismiss=lambda e: print(""))
            page.open(alerta_excepcion)

    # Funcion para actualizar la tabla
    def actualizar_tabla():
        # Actualiza las filas de la tabla con los nuevos valores
        dashboard_tabla.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Zanahoria")),
                    ft.DataCell(ft.Text(zanahoria))
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Berenjena")),
                    ft.DataCell(ft.Text(berenjena))
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Patata")),
                    ft.DataCell(ft.Text(patata))
                ]
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Tomate")),
                    ft.DataCell(ft.Text(tomate))
                ]
            )
        ]

        # Crear el grafico de pastel
        grafico_labels = ["Zanahoria", "Berenjena", "Patata", "Tomate"]
        grafico_data = [zanahoria, berenjena, patata, tomate]
        grafico_colors = ["#ee6c4d", "#6d597a", "#f9c74f", "#e56b6f"]

        # Filtrar los datos para excluir las hortalizas con valor 0
        filtered_labels = [label for label, data in zip(grafico_labels, grafico_data) if data > 0]
        filtered_data = [data for data in grafico_data if data > 0]
        filtered_colors = [color for color, data in zip(grafico_colors, grafico_data) if data > 0]

        if filtered_data:  # Solo crear el gráfico si hay datos
            fig, ax = plt.subplots()
            ax.pie(filtered_data, labels=filtered_labels, colors=filtered_colors, autopct='%1.0f%%')
            ax.axis("equal")
            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            grafico_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            buf.close()
            dashboard_grafico.src_base64 = grafico_base64

        page.update()

    # FilePicker para seleccionar los archivos
    file_picker = ft.FilePicker(on_result=seleccionar_archivo)
    page.overlay.append(file_picker)

    # Header
    header = ft.Text("AgroVision", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)

    # Boton para cambiar el tema
    tema_boton = ft.ElevatedButton(text="Cambiar el Tema", icon="sunny", on_click=cambiar_tema, bgcolor="#4C956C", color="#ffffff")

    # Boton para cerrar sesion
    cerrar_sesion_boton = ft.ElevatedButton(text="Cerrar Sesión", icon="logout", on_click=cerrar_sesion, bgcolor="#4C956C", color="#ffffff")

    # Boton para cargar una imagen
    cargar_boton = ft.ElevatedButton(text="Cargar Imagen", icon="folder_open", on_click=lambda _: file_picker.pick_files(), bgcolor="#4C956C", color="#ffffff")

    # Boton para guardar
    guardar_boton = ft.ElevatedButton(text="Guardar Detección", icon="save", on_click=guardar_resultados, bgcolor="#4C956C", color="#ffffff")

    # Mensaje de bienvenida
    bienvenida_mensaje = ft.Text(value=f"Bienvenido {informacion_usuario[1][1]}", size=20, text_align=ft.TextAlign.CENTER)

    # Contenedores
    # Contenedor de la detección
    global contenedor_deteccion
    contenedor_deteccion = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 125,
    )

    # Tabla del dashboard
    global dashboard_tabla
    dashboard_tabla = ft.DataTable(
        heading_row_color=ft.colors.BLACK12,
        columns=[
            ft.DataColumn(ft.Text("Hortaliza")),
            ft.DataColumn(ft.Text("# de Detecciones"), numeric=True)
        ],
        rows=[]
    )

    # Grafico de pastel
    global dashboard_grafico
    dashboard_grafico = ft.Image(height=ft.ImageFit.FIT_HEIGHT)

    # Contenedor del dashboard
    contenedor_dashboard = ft.Container(
        width=page.window_width * 0.45,  # El 45% de la ventana
        height=page.window_height - 30,
        content=ft.Column([
            dashboard_tabla,
            dashboard_grafico
        ])
    )

    # Agregar los componentes a la página
    page.add(
        ft.Column(
            [
                ft.Row([header], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([bienvenida_mensaje], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([tema_boton, cargar_boton, guardar_boton, cerrar_sesion_boton], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Row([contenedor_deteccion, contenedor_dashboard], alignment=ft.MainAxisAlignment.CENTER),
            ]
        )
    )

ft.app(target=main)
