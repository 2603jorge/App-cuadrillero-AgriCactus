# =============================================================================
#  AgriCactus - App del CUADRILLERO  (main.py)
#  v2.6 - Fix indentacion iniciar_escaneo_ble
# =============================================================================

import datetime
import json
import os
import socket
import threading

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget

try:
    from plyer import gps, filechooser
    GPS_DISPONIBLE = True
except Exception:
    GPS_DISPONIBLE = False

if platform == 'android':
    try:
        from jnius import autoclass, PythonJavaClass, java_method
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        ScanSettings     = autoclass('android.bluetooth.le.ScanSettings')

        class _ScanCallback(PythonJavaClass):
            __javainterfaces__ = ['android/bluetooth/le/ScanCallback']
            __javacontext__ = 'app'

            def __init__(self, on_encontrado):
                super().__init__()
                self._on_encontrado = on_encontrado

            @java_method('(ILandroid/bluetooth/le/ScanResult;)V')
            def onScanResult(self, callbackType, result):
                uuid = None
                sr = result.getScanRecord()
                if sr:
                    uuids = sr.getServiceUuids()
                    if uuids and not uuids.isEmpty():
                        uuid = str(uuids.get(0).getUuid())
                Clock.schedule_once(
                    lambda dt: self._on_encontrado(uuid, result.getRssi()), 0
                )

            @java_method('(Ljava/util/List;)V')
            def onBatchScanResults(self, results):
                pass

            @java_method('(II)V')
            def onScanFailed(self, errorCode):
                print(f"[BLE SCAN] Error: {errorCode}")

        BLE_SCAN_DISPONIBLE = True
    except Exception as e:
        print(f"[BLE] No disponible: {e}")
        BLE_SCAN_DISPONIBLE = False
else:
    BLE_SCAN_DISPONIBLE = False

ARCHIVO_DATOS      = "cuadrillero_data.json"
ARCHIVO_LISTA      = "lista_asistencia.json"
PUERTO_WIFI        = 45678
PUERTO_CUADRILLERO = 45679
PUERTO_RECEPCION   = 45680
UUID_PREFIX        = "0000ac10-0000-1000-8000-"


def guardar_datos(datos: dict):
    try:
        with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[STORAGE] Error: {e}")


def cargar_datos() -> dict:
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def guardar_lista(datos: dict):
    try:
        with open(ARCHIVO_LISTA, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[STORAGE] Error lista: {e}")


KV = '''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import FitImage kivymd.uix.fitimage.FitImage

ScreenManager:
    transition: FadeTransition()
    PantallaRegistro:
    PantallaCredencial:
    PantallaAsistencia:
    PantallaResumen:


<PantallaRegistro>:
    name: 'registro'

    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDFloatLayout:
            size_hint_y: 0.15
            pos_hint: {'x': 0, 'top': 1}
            md_bg_color: 0.18, 0.29, 0.12, 1

            Image:
                source: "logo_agricactus.png"
                size_hint: (0.38, 0.80)
                allow_stretch: True
                keep_ratio: True
                pos_hint: {'center_x': 0.22, 'center_y': 0.5}

            MDLabel:
                text: "REGISTRO CUADRILLERO"
                font_style: "H6"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {'center_x': 0.64, 'center_y': 0.5}
                size_hint: (0.6, 1)

        MDBoxLayout:
            size_hint_y: 0.006
            pos_hint: {'x': 0, 'top': 0.85}
            md_bg_color: 0.96, 0.65, 0.14, 1

        MDTextField:
            id: input_nombre
            hint_text: "Nombre Completo"
            helper_text: "Se convertira a MAYUSCULAS"
            helper_text_mode: "on_focus"
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.76}
            size_hint_x: 0.88

        MDTextField:
            id: input_nss
            hint_text: "Numero de Seguro Social (NSS)"
            max_text_length: 11
            input_filter: "int"
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.65}
            size_hint_x: 0.88

        MDTextField:
            id: input_credencial
            hint_text: "Numero de Credencial / Empleado"
            input_filter: "int"
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
            size_hint_x: 0.88

        MDTextField:
            id: input_cuadrilla
            hint_text: "Numero de Cuadrilla a cargo"
            input_filter: "int"
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.45}
            size_hint_x: 0.88

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint: (0.88, 0.07)
            pos_hint: {'center_x': 0.5, 'center_y': 0.35}
            spacing: '8dp'

            MDRectangleFlatIconButton:
                icon: "camera"
                text: "CAMARA"
                theme_text_color: "Custom"
                text_color: 0.18, 0.29, 0.12, 1
                line_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.5
                on_release: root.tomar_foto()

            MDRectangleFlatIconButton:
                icon: "image"
                text: "GALERIA"
                theme_text_color: "Custom"
                text_color: 0.18, 0.29, 0.12, 1
                line_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.5
                on_release: root.abrir_galeria()

        MDLabel:
            id: label_foto
            text: "Sin foto seleccionada"
            font_style: "Caption"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.26}

        MDRaisedButton:
            text: "GENERAR CREDENCIAL DIGITAL"
            md_bg_color: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.14}
            size_hint_x: 0.88
            elevation: 4
            on_release: root.guardar_registro()


<PantallaCredencial>:
    name: 'credencial'

    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDFloatLayout:
            size_hint_x: 0.06
            pos_hint: {'x': 0, 'y': 0}
            md_bg_color: 0.18, 0.29, 0.12, 1

        MDCard:
            size_hint: (0.92, 0.72)
            pos_hint: {'right': 0.99, 'top': 0.97}
            elevation: 3
            radius: [12, 12, 12, 12]
            md_bg_color: 1, 1, 1, 1

            MDFloatLayout:

                MDFloatLayout:
                    size_hint_y: 0.20
                    pos_hint: {'x': 0, 'top': 1}
                    md_bg_color: 0.18, 0.29, 0.12, 1

                    Image:
                        source: "logo_agricactus.png"
                        size_hint: (0.48, 0.82)
                        allow_stretch: True
                        keep_ratio: True
                        pos_hint: {'center_x': 0.28, 'center_y': 0.5}

                    MDLabel:
                        text: "CUADRILLERO"
                        font_style: "Caption"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.96, 0.65, 0.14, 1
                        pos_hint: {'center_x': 0.74, 'center_y': 0.65}
                        size_hint: (0.5, 0.2)

                    MDLabel:
                        text: "CREDENCIAL DIGITAL"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.8, 0.9, 0.8, 1
                        pos_hint: {'center_x': 0.74, 'center_y': 0.35}
                        size_hint: (0.5, 0.2)

                FitImage:
                    source: root.ruta_foto
                    size_hint: (0.34, 0.38)
                    pos_hint: {'x': 0.04, 'center_y': 0.57}
                    radius: [8, 8, 8, 8]

                MDLabel:
                    text: root.nombre_cuadrillero
                    markup: True
                    font_style: "H6"
                    bold: True
                    halign: "left"
                    valign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.29, 0.12, 1
                    text_size: self.size
                    pos_hint: {'x': 0.42, 'center_y': 0.64}
                    size_hint: (0.55, 0.18)

                MDLabel:
                    text: "Ingreso: " + root.fecha_ingreso
                    font_style: "Caption"
                    halign: "left"
                    theme_text_color: "Secondary"
                    pos_hint: {'x': 0.42, 'center_y': 0.53}
                    size_hint: (0.55, 0.06)

                MDLabel:
                    text: "Cuadrilla a cargo: " + root.num_cuadrilla
                    font_style: "Body2"
                    bold: True
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0.29, 0.40, 0.25, 1
                    pos_hint: {'x': 0.42, 'center_y': 0.46}
                    size_hint: (0.55, 0.06)

                MDBoxLayout:
                    size_hint: (0.88, 0.005)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.38}
                    md_bg_color: 0.96, 0.65, 0.14, 1

                MDLabel:
                    text: "NSS: " + root.nss
                    font_style: "Body2"
                    bold: True
                    halign: "left"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.29, 0.12, 1
                    pos_hint: {'x': 0.06, 'center_y': 0.32}
                    size_hint: (0.5, 0.06)

                MDLabel:
                    text: "No. " + root.num_credencial
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.29, 0.12, 1
                    pos_hint: {'center_x': 0.5, 'center_y': 0.22}
                    size_hint: (0.88, 0.08)

                MDFloatLayout:
                    size_hint_y: 0.05
                    pos_hint: {'x': 0, 'y': 0}
                    md_bg_color: 0.18, 0.29, 0.12, 1
                    MDLabel:
                        text: "Blvd. Kino 309, Piso 6 - Hermosillo, Sonora"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.8, 0.9, 0.8, 1

        MDRaisedButton:
            text: "INICIAR JORNADA"
            md_bg_color: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.55, 'y': 0.16}
            size_hint: (0.80, 0.07)
            elevation: 4
            on_release: root.ir_a_asistencia()

        MDRectangleFlatButton:
            text: "EDITAR DATOS"
            theme_text_color: "Custom"
            text_color: 0.18, 0.29, 0.12, 1
            line_color: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.55, 'y': 0.07}
            size_hint: (0.80, 0.07)
            on_release: app.root.current = 'registro'


<PantallaAsistencia>:
    name: 'asistencia'

    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDFloatLayout:
            size_hint_y: 0.13
            pos_hint: {'x': 0, 'top': 1}
            md_bg_color: 0.18, 0.29, 0.12, 1

            Image:
                source: "logo_agricactus.png"
                size_hint: (0.28, 0.80)
                allow_stretch: True
                keep_ratio: True
                pos_hint: {'center_x': 0.16, 'center_y': 0.5}

            MDLabel:
                text: root.titulo_sesion
                font_style: "Body1"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {'center_x': 0.58, 'center_y': 0.60}
                size_hint: (0.66, 0.4)

            MDLabel:
                text: root.fecha_hoy
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.96, 0.65, 0.14, 1
                pos_hint: {'center_x': 0.58, 'center_y': 0.28}
                size_hint: (0.66, 0.3)

        MDBoxLayout:
            size_hint_y: 0.005
            pos_hint: {'x': 0, 'top': 0.87}
            md_bg_color: 0.96, 0.65, 0.14, 1

        MDTextField:
            id: input_cuadro
            hint_text: "Cuadro / Lote de trabajo"
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'top': 0.86}
            size_hint: (0.96, None)
            height: '48dp'

        MDCard:
            size_hint: (0.96, 0.10)
            pos_hint: {'center_x': 0.5, 'top': 0.75}
            elevation: 2
            radius: [8, 8, 8, 8]
            md_bg_color: 1, 1, 1, 1

            MDBoxLayout:
                orientation: 'horizontal'
                padding: '8dp'
                spacing: '4dp'

                MDBoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        text: root.total_presentes
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.18, 0.29, 0.12, 1
                    MDLabel:
                        text: "Presentes"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Secondary"

                MDBoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        text: root.total_detectados
                        font_style: "H5"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 0.96, 0.65, 0.14, 1
                    MDLabel:
                        text: "Detectados"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Secondary"

                MDBoxLayout:
                    orientation: 'vertical'
                    MDLabel:
                        text: root.estado_escaneo
                        font_style: "Caption"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: root.color_estado_escaneo
                    MDLabel:
                        text: "Estado BLE"
                        font_style: "Caption"
                        halign: "center"
                        theme_text_color: "Secondary"

        MDCard:
            size_hint: (0.96, 0.44)
            pos_hint: {'center_x': 0.5, 'top': 0.64}
            elevation: 2
            radius: [8, 8, 8, 8]
            md_bg_color: 1, 1, 1, 1

            MDBoxLayout:
                orientation: 'vertical'
                padding: '4dp'

                MDLabel:
                    text: "Trabajadores detectados"
                    font_style: "Caption"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.29, 0.12, 1
                    size_hint_y: None
                    height: '28dp'

                ScrollView:
                    MDList:
                        id: lista_trabajadores

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint: (0.96, 0.08)
            pos_hint: {'center_x': 0.5, 'y': 0.09}
            spacing: '6dp'

            MDRaisedButton:
                text: "VALIDAR TODOS"
                md_bg_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.34
                elevation: 3
                on_release: root.validar_todos()

            MDRaisedButton:
                text: "VER RESUMEN"
                md_bg_color: 0.96, 0.65, 0.14, 1
                text_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.33
                elevation: 3
                on_release: root.ver_resumen()

            MDRaisedButton:
                text: "TEST"
                md_bg_color: 0.29, 0.40, 0.25, 1
                size_hint_x: 0.33
                elevation: 3
                on_release: app.test_scan()

        MDRectangleFlatButton:
            text: "MI CREDENCIAL"
            theme_text_color: "Custom"
            text_color: 0.18, 0.29, 0.12, 1
            line_color: 0.18, 0.29, 0.12, 1
            size_hint: (0.96, 0.07)
            pos_hint: {'center_x': 0.5, 'y': 0.01}
            on_release: app.root.current = 'credencial'


<PantallaResumen>:
    name: 'resumen'

    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDFloatLayout:
            size_hint_y: 0.13
            pos_hint: {'x': 0, 'top': 1}
            md_bg_color: 0.18, 0.29, 0.12, 1

            MDLabel:
                text: "RESUMEN DEL DIA"
                font_style: "H6"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.96, 0.65, 0.14, 1
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint: (1, 1)

        MDBoxLayout:
            size_hint_y: 0.005
            pos_hint: {'x': 0, 'top': 0.87}
            md_bg_color: 0.96, 0.65, 0.14, 1

        MDCard:
            size_hint: (0.96, 0.70)
            pos_hint: {'center_x': 0.5, 'top': 0.85}
            elevation: 2
            radius: [8, 8, 8, 8]
            md_bg_color: 1, 1, 1, 1

            MDBoxLayout:
                orientation: 'vertical'
                padding: '12dp'
                spacing: '8dp'

                MDLabel:
                    text: root.resumen_texto
                    font_style: "Body1"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.18, 0.29, 0.12, 1
                    size_hint_y: None
                    height: '72dp'

                ScrollView:
                    MDList:
                        id: lista_resumen

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint: (0.96, 0.08)
            pos_hint: {'center_x': 0.5, 'y': 0.01}
            spacing: '8dp'

            MDRaisedButton:
                text: "GUARDAR LISTA"
                md_bg_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.5
                elevation: 3
                on_release: root.guardar_lista_dia()

            MDRaisedButton:
                text: "REGRESAR"
                md_bg_color: 0.96, 0.65, 0.14, 1
                text_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.5
                elevation: 3
                on_release: app.root.current = 'asistencia'
'''


class PantallaRegistro(Screen):
    ruta_foto_seleccionada = ""
    _ruta_foto_camara      = ""

    def tomar_foto(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                from android import activity as android_activity
                from jnius import autoclass
                request_permissions([
                    Permission.CAMERA,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
                Intent         = autoclass('android.content.Intent')
                MediaStore     = autoclass('android.provider.MediaStore')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                PythonActivity.mActivity.startActivityForResult(intent, 1001)
                android_activity.bind(on_activity_result=self._resultado_camara)
            except Exception as e:
                self.ids.label_foto.text = f"Error camara: {e}"
        else:
            self.ids.label_foto.text = "Camara solo disponible en Android"

    def _resultado_camara(self, requestCode, resultCode, intent):
        RESULT_OK = -1
        if requestCode != 1001 or resultCode != RESULT_OK:
            self.ids.label_foto.text = "Foto cancelada"
            return
        try:
            from jnius import autoclass
            PythonActivity       = autoclass('org.kivy.android.PythonActivity')
            FileOutputStream     = autoclass('java.io.FileOutputStream')
            BitmapCompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
            extras    = intent.getExtras()
            bitmap    = extras.get("data")
            files_dir = PythonActivity.mActivity.getFilesDir().getAbsolutePath()
            ruta      = f"{files_dir}/cuadrillero_foto.jpg"
            fos = FileOutputStream(ruta)
            bitmap.compress(BitmapCompressFormat.JPEG, 90, fos)
            fos.close()
            self.ruta_foto_seleccionada = ruta
            self.ids.label_foto.text    = "Foto tomada correctamente"
        except Exception as e:
            self.ids.label_foto.text = f"Error guardando foto: {e}"

    def abrir_galeria(self):
        if GPS_DISPONIBLE:
            try:
                from plyer import filechooser as fc
                fc.open_file(
                    title="Selecciona tu foto de perfil",
                    filters=[("Imagenes", "*.jpg", "*.jpeg", "*.png")],
                    on_selection=self.al_seleccionar_foto
                )
            except Exception as e:
                self.ids.label_foto.text = f"Error galeria: {e}"
        else:
            self.ids.label_foto.text = "Galeria no disponible en escritorio"

    def al_seleccionar_foto(self, seleccion):
        if seleccion:
            self.ruta_foto_seleccionada = seleccion[0]
            self.ids.label_foto.text    = f"OK: {os.path.basename(seleccion[0])}"

    def guardar_registro(self):
        nombre     = self.ids.input_nombre.text.strip().upper()
        nss        = self.ids.input_nss.text.strip()
        credencial = self.ids.input_credencial.text.strip()
        cuadrilla  = self.ids.input_cuadrilla.text.strip()

        errores = []
        if not nombre:
            errores.append("nombre")
        if len(nss) < 10:
            errores.append("NSS valido (min 10 digitos)")
        if not credencial:
            errores.append("numero de credencial")
        if not cuadrilla:
            errores.append("numero de cuadrilla")
        if not self.ruta_foto_seleccionada:
            errores.append("foto")

        if errores:
            Snackbar(text=f"Falta: {', '.join(errores)}").open()
            return

        app = MDApp.get_running_app()
        pc  = app.root.get_screen('credencial')

        palabras = nombre.split()
        if len(palabras) >= 3:
            nombre_fmt = f"{palabras[0]} {palabras[1]}\n{' '.join(palabras[2:])}"
        elif len(palabras) == 2:
            nombre_fmt = f"{palabras[0]}\n{palabras[1]}"
        else:
            nombre_fmt = nombre

        pc.nombre_cuadrillero = nombre_fmt
        pc.nss                = nss
        pc.num_credencial     = credencial
        pc.num_cuadrilla      = cuadrilla
        pc.ruta_foto          = self.ruta_foto_seleccionada
        pc.fecha_ingreso      = datetime.date.today().strftime("%d/%m/%Y")

        app.num_cuadrilla      = cuadrilla
        app.nombre_cuadrillero = nombre_fmt

        datos = {
            "nombre":        nombre_fmt,
            "nss":           nss,
            "credencial":    credencial,
            "cuadrilla":     cuadrilla,
            "foto":          self.ruta_foto_seleccionada,
            "fecha_ingreso": pc.fecha_ingreso,
            "ultima_sesion": datetime.datetime.now().isoformat()
        }
        guardar_datos(datos)
        app.root.current = 'credencial'
        Snackbar(text="Credencial generada correctamente").open()


class PantallaCredencial(Screen):
    nombre_cuadrillero = StringProperty("")
    fecha_ingreso      = StringProperty("")
    nss                = StringProperty("")
    num_credencial     = StringProperty("")
    num_cuadrilla      = StringProperty("")
    ruta_foto          = StringProperty("")

    def ir_a_asistencia(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission, check_permission
                from jnius import autoclass as _ac
                BuildVersion = _ac('android.os.Build$VERSION')
                sdk = BuildVersion.SDK_INT

                if sdk >= 31:
                    permisos_necesarios = [
                        Permission.BLUETOOTH_SCAN,
                        Permission.BLUETOOTH_CONNECT,
                        Permission.ACCESS_FINE_LOCATION,
                    ]
                else:
                    permisos_necesarios = [
                        Permission.BLUETOOTH,
                        Permission.ACCESS_FINE_LOCATION,
                    ]

                todos_concedidos = all(
                    check_permission(p) for p in permisos_necesarios
                )
                Snackbar(text=f"SDK:{sdk} Permisos:{todos_concedidos}").open()

                if not todos_concedidos:
                    def _on_permisos(permisos, concedidos):
                        if all(concedidos):
                            Clock.schedule_once(
                                lambda dt: self._continuar_a_asistencia(), 0.5
                            )
                        else:
                            Snackbar(text="Acepta TODOS los permisos").open()
                    request_permissions(permisos_necesarios, _on_permisos)
                    return

            except Exception as e:
                Snackbar(text=f"Error permisos: {e}").open()
                print(f"[PERMISOS] Error: {e}")

        self._continuar_a_asistencia()

    def _continuar_a_asistencia(self):
        Snackbar(text="Iniciando jornada...").open()
        app = MDApp.get_running_app()
        pa  = app.root.get_screen('asistencia')
        pa.titulo_sesion = f"Cuadrilla {self.num_cuadrilla}"
        pa.fecha_hoy     = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
        app.iniciar_escaneo_ble()
        app.iniciar_respuesta_apuntador()
        app.root.current = 'asistencia'


class PantallaAsistencia(Screen):
    titulo_sesion        = StringProperty("Cuadrilla")
    fecha_hoy            = StringProperty("")
    total_presentes      = StringProperty("0")
    total_detectados     = StringProperty("0")
    estado_escaneo       = StringProperty("Inactivo")
    color_estado_escaneo = ListProperty([0.6, 0.6, 0.6, 1])

    def actualizar_lista_ui(self, trabajadores: dict):
        self.ids.lista_trabajadores.clear_widgets()
        presentes = 0
        for credencial, info in trabajadores.items():
            validado = info.get('validado', False)
            nombre   = info.get('nombre', f"Cred. {credencial}")
            hora     = info.get('hora_deteccion', '--:--')
            rssi     = info.get('rssi', 0)
            if validado:
                presentes += 1
            icono = IconLeftWidget(
                icon="check-circle" if validado else "bluetooth",
                theme_text_color="Custom",
                icon_color=(0.18, 0.29, 0.12, 1) if validado else (0.96, 0.65, 0.14, 1)
            )
            item = TwoLineIconListItem(
                text=f"[b]{nombre}[/b]  |  No. {credencial}",
                secondary_text=(
                    f"Detectado: {hora}  |  Senal: {rssi} dBm  |  "
                    f"{'VALIDADO' if validado else 'Pendiente'}"
                ),
            )
            item.add_widget(icono)
            self.ids.lista_trabajadores.add_widget(item)
        self.total_presentes  = str(presentes)
        self.total_detectados = str(len(trabajadores))

    def validar_todos(self):
        app   = MDApp.get_running_app()
        count = 0
        for cred in list(app.trabajadores_detectados.keys()):
            if not app.trabajadores_detectados[cred].get('validado'):
                app.enviar_validacion_wifi(cred)
                count += 1
        Snackbar(
            text=f"{count} trabajador(es) validados" if count
            else "Todos ya estan validados"
        ).open()

    def ver_resumen(self):
        app    = MDApp.get_running_app()
        cuadro = self.ids.input_cuadro.text.strip().upper() or "SIN CUADRO"
        pr     = app.root.get_screen('resumen')
        pr.construir_resumen(
            app.trabajadores_detectados,
            app.nombre_cuadrillero,
            app.num_cuadrilla,
            cuadro
        )
        app.cuadro_trabajo = cuadro
        app.root.current   = 'resumen'


class PantallaResumen(Screen):
    resumen_texto = StringProperty("")

    def construir_resumen(self, trabajadores, cuadrillero, cuadrilla, cuadro):
        presentes = sum(1 for v in trabajadores.values() if v.get('validado'))
        total     = len(trabajadores)
        fecha     = datetime.datetime.now().strftime("%d/%m/%Y")
        self.resumen_texto = (
            f"Cuadrilla {cuadrilla} | {cuadro}\n"
            f"{cuadrillero}  |  {fecha}\n"
            f"Presentes: {presentes} / {total}"
        )
        self.ids.lista_resumen.clear_widgets()
        for cred, info in trabajadores.items():
            validado = info.get('validado', False)
            icono = IconLeftWidget(
                icon="check" if validado else "close",
                theme_text_color="Custom",
                icon_color=(0.18, 0.29, 0.12, 1) if validado else (0.72, 0.10, 0.10, 1)
            )
            item = TwoLineIconListItem(
                text=f"Cred. {cred}  —  {info.get('nombre', '')}",
                secondary_text=(
                    info.get('hora_deteccion', '--') +
                    ('  ✓ PRESENTE' if validado else '  ✗ AUSENTE')
                ),
            )
            item.add_widget(icono)
            self.ids.lista_resumen.add_widget(item)

    def guardar_lista_dia(self):
        app   = MDApp.get_running_app()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        datos = {
            "fecha":        fecha,
            "cuadrillero":  app.nombre_cuadrillero,
            "cuadrilla":    app.num_cuadrilla,
            "cuadro":       app.cuadro_trabajo,
            "trabajadores": app.trabajadores_detectados
        }
        guardar_lista(datos)
        Snackbar(text="Lista guardada correctamente").open()


class CuadrilleroAgriCactusApp(MDApp):
    nombre_cuadrillero      = ""
    num_cuadrilla           = ""
    cuadro_trabajo          = ""
    trabajadores_detectados = {}
    _ble_scanner            = None
    _scan_callback          = None
    _escaneo_activo         = False

    def build(self):
        self.theme_cls.theme_style     = "Light"
        self.theme_cls.primary_palette = "Green"
        controlador = Builder.load_string(KV)
        Clock.schedule_once(self._restaurar_sesion, 0.5)
        return controlador

    def _restaurar_sesion(self, dt):
        datos = cargar_datos()
        if not datos:
            return
        pc = self.root.get_screen('credencial')
        pc.nombre_cuadrillero = datos.get("nombre", "")
        pc.nss                = datos.get("nss", "")
        pc.num_credencial     = datos.get("credencial", "")
        pc.num_cuadrilla      = datos.get("cuadrilla", "")
        pc.ruta_foto          = datos.get("foto", "")
        pc.fecha_ingreso      = datos.get("fecha_ingreso", "")
        self.num_cuadrilla      = datos.get("cuadrilla", "")
        self.nombre_cuadrillero = datos.get("nombre", "")
        self.root.current = 'credencial'

    def test_scan(self):
        ble_ok     = BLE_SCAN_DISPONIBLE
        scan_ok    = self._ble_scanner is not None
        activo     = self._escaneo_activo
        cuadrilla  = self.num_cuadrilla
        detectados = len(self.trabajadores_detectados)
        msg = f"BLE:{ble_ok} Scan:{scan_ok} Act:{activo} C:{cuadrilla} Det:{detectados}"
        Snackbar(text=msg).open()
        print(f"[TEST CUADRILLERO] {msg}")

    def iniciar_escaneo_ble(self):
        if not BLE_SCAN_DISPONIBLE:
            self._simular_deteccion_escritorio()
            return
        try:
            if platform == 'android':
                from android.permissions import check_permission, Permission
                from jnius import autoclass as _ac
                sdk = _ac('android.os.Build$VERSION').SDK_INT
                if sdk >= 31:
                    if not check_permission(Permission.BLUETOOTH_SCAN):
                        Snackbar(text="Falta permiso BLUETOOTH_SCAN").open()
                        return
                else:
                    if not check_permission(Permission.BLUETOOTH):
                        Snackbar(text="Falta permiso BLUETOOTH").open()
                        return
                if not check_permission(Permission.ACCESS_FINE_LOCATION):
                    Snackbar(text="Falta permiso de ubicacion").open()
                    return

            adaptador = BluetoothAdapter.getDefaultAdapter()
            if not adaptador:
                Snackbar(text="Dispositivo sin Bluetooth").open()
                return
            if not adaptador.isEnabled():
                Snackbar(text="Activa el Bluetooth").open()
                return

            self._ble_scanner = adaptador.getBluetoothLeScanner()
            if not self._ble_scanner:
                Snackbar(text="BLE Scanner no disponible").open()
                return

            self._scan_callback = _ScanCallback(self._al_detectar_ble)
            sb = ScanSettings.Builder()
            sb.setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            settings = sb.build()

            try:
                self._ble_scanner.startScan(None, settings, self._scan_callback)
                self._escaneo_activo = True
                pa = self.root.get_screen('asistencia')
                pa.estado_escaneo       = "Activo"
                pa.color_estado_escaneo = [0.18, 0.29, 0.12, 1]
                Snackbar(text="Escaneo BLE iniciado OK").open()
            except Exception as e:
                Snackbar(text=f"startScan fallo: {e}").open()
                print(f"[BLE] startScan error: {e}")

        except Exception as e:
            print(f"[BLE SCAN] Error: {e}")
            Snackbar(text=f"Error BLE: {e}").open()

    def detener_escaneo_ble(self):
        if BLE_SCAN_DISPONIBLE and self._ble_scanner and self._scan_callback:
            try:
                self._ble_scanner.stopScan(self._scan_callback)
                self._escaneo_activo = False
            except Exception as e:
                print(f"[BLE SCAN] Error al detener: {e}")

    def _al_detectar_ble(self, uuid_str, rssi):
        if not uuid_str or not uuid_str.startswith(UUID_PREFIX):
            return
        try:
            sufijo              = uuid_str.replace(UUID_PREFIX, "")
            cuadrilla_detectada = str(int(sufijo[:3]))
            credencial          = str(int(sufijo[3:]))
        except Exception:
            return
        if cuadrilla_detectada != str(self.num_cuadrilla):
            return
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        if credencial not in self.trabajadores_detectados:
            self.trabajadores_detectados[credencial] = {
                "nombre":         f"Trabajador {credencial}",
                "hora_deteccion": ahora,
                "rssi":           rssi,
                "validado":       False,
                "ip":             None
            }
        else:
            self.trabajadores_detectados[credencial]["rssi"] = rssi
        self._actualizar_ui()

    def _actualizar_ui(self):
        pa = self.root.get_screen('asistencia')
        if self.root.current == 'asistencia':
            pa.actualizar_lista_ui(self.trabajadores_detectados)

    def enviar_validacion_wifi(self, credencial):
        fecha   = datetime.datetime.now().strftime("%Y-%m-%d")
        mensaje = f"VALIDAR:{credencial}:{self.num_cuadrilla}:{fecha}"

        def _enviar():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(3.0)
                    sock.sendto(mensaje.encode('utf-8'), ('255.255.255.255', PUERTO_WIFI))
                    try:
                        resp_raw, addr = sock.recvfrom(256)
                        resp = resp_raw.decode('utf-8').strip()
                        if resp.startswith(f"OK:{credencial}"):
                            Clock.schedule_once(
                                lambda dt: self._confirmar_validacion(credencial, addr[0]), 0
                            )
                    except socket.timeout:
                        Clock.schedule_once(
                            lambda dt: self._confirmar_validacion(credencial, None), 0
                        )
            except Exception as e:
                print(f"[WIFI] Error enviando: {e}")

        threading.Thread(target=_enviar, daemon=True).start()

    def _confirmar_validacion(self, credencial, ip):
        if credencial in self.trabajadores_detectados:
            self.trabajadores_detectados[credencial]['validado']        = True
            self.trabajadores_detectados[credencial]['hora_validacion'] = \
                datetime.datetime.now().strftime("%H:%M:%S")
            if ip:
                self.trabajadores_detectados[credencial]['ip'] = ip
        self._actualizar_ui()

    def iniciar_respuesta_apuntador(self):
        def _escuchar():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('', PUERTO_CUADRILLERO))
                    sock.settimeout(2.0)
                    while True:
                        try:
                            datos_raw, addr = sock.recvfrom(1024)
                            mensaje = datos_raw.decode('utf-8').strip()
                            if mensaje.startswith('PEDIR_LISTA:'):
                                Clock.schedule_once(
                                    lambda dt, a=addr, s=sock:
                                    self._enviar_lista_apuntador(s, a), 0
                                )
                        except socket.timeout:
                            continue
                        except Exception as e:
                            print(f"[WIFI] Error escucha apuntador: {e}")
            except Exception as e:
                print(f"[WIFI] Error servidor apuntador: {e}")

        threading.Thread(target=_escuchar, daemon=True).start()

    def _enviar_lista_apuntador(self, sock, addr):
        payload = {
            "tipo":         "LISTA_CUADRILLA",
            "cuadrilla":    self.num_cuadrilla,
            "cuadrillero":  self.nombre_cuadrillero,
            "cuadro":       self.cuadro_trabajo,
            "fecha":        datetime.datetime.now().strftime("%Y-%m-%d"),
            "trabajadores": self.trabajadores_detectados
        }
        try:
            datos = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            sock.sendto(datos, (addr[0], PUERTO_RECEPCION))
            Snackbar(text="Lista enviada al apuntador").open()
        except Exception as e:
            print(f"[WIFI] Error enviando lista: {e}")

    def _simular_deteccion_escritorio(self):
        pa = self.root.get_screen('asistencia')
        pa.estado_escaneo       = "Simulado"
        pa.color_estado_escaneo = [0.96, 0.65, 0.14, 1]

        def _agregar_demo(dt):
            demos = [
                ("1001", "GARCIA LOPEZ JUAN"),
                ("1002", "MARTINEZ RUIZ PEDRO"),
                ("1003", "HERNANDEZ SOTO ANA"),
            ]
            for cred, nombre in demos:
                if cred not in self.trabajadores_detectados:
                    self.trabajadores_detectados[cred] = {
                        "nombre":         nombre,
                        "hora_deteccion": datetime.datetime.now().strftime("%H:%M:%S"),
                        "rssi":           -65,
                        "validado":       False,
                        "ip":             None
                    }
            self._actualizar_ui()

        Clock.schedule_once(_agregar_demo, 2.0)

    def on_stop(self):
        self.detener_escaneo_ble()


if __name__ == '__main__':
    CuadrilleroAgriCactusApp().run()
