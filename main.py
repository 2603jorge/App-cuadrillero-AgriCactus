# =============================================================================
#  AgriCactus - App del CUADRILLERO  (main.py)
#  v3.1 - Cuadro+Actividad separados + buscador actividades + señal apuntador
# =============================================================================

import datetime
import json
import os
import socket
import threading

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, OneLineListItem

# =============================================================================
#  CATALOGO DE ACTIVIDADES
# =============================================================================
ACTIVIDADES = [
    ("1000","APOYO CAMPO AGUA"),("1001","APOYO CAMPO BAÑOS"),
    ("1002","APOYO CAMPO BASURA"),("1003","APOYO CAMPO RANCHO"),
    ("1004","APOYO CAMPO TALLER"),("1005","APOYO CAMPO ASISTENCIA"),
    ("1006","APOYO CAMPO LIMPIEZA"),("1007","APOYO CAMPO LIMPIEZA GUARDERIA"),
    ("1008","PIPA"),("1009","TRANSPORTE PERSONAL"),("1010","TROQUE/CAMION"),
    ("1011","BATANGA AGUA"),("1012","BATANGA BOMBA BAÑOS"),("1013","BATANGA RESAGA"),
    ("1014","SUBSUELO"),("1015","PREPODA"),("1016","MOLINO RANCHO"),
    ("1017","MEZCLADORA ALIMENTO RANCHO"),("1018","SEMBRADORA"),("1019","BATANGA"),
    ("1020","APLICADORA FOLIAR"),("1021","ARADO/BARVECHO"),("1022","RASTRA"),
    ("1023","TABLON"),("1024","BORDERO CINTA Y ACOLCHADO"),("1025","ESCREPA"),
    ("1026","APLICADORA HERBICIDA"),("1027","HAYBINE"),("1028","CORTADORA DE DISCOS"),
    ("1029","RASTRILLO"),("1030","EMPACADORA"),("1031","MONTAGARGA CALABAZA"),
    ("1032","APLICACION MOCHILA"),("1033","AUXILIAR DE RIEGO"),("1034","REGADOR"),
    ("1035","SUPERVISOR DE RIEGO"),("1036","PODA DIA"),("1037","PODA ENSAYO"),
    ("1038","CUADRILLERO"),("1039","SUPERVISOR"),("1040","SUPERVISOR GENERAL"),
    ("1041","SUPERVISOR GENERAL 1"),("1042","SUPERVISOR RECLUTADOR 2"),
    ("1043","SUPERVISOR RECLUTADOR 3"),("1044","SUPERVISOR RECLUTADOR 4"),
    ("1045","SACAR PLANTAS UVA"),("1046","DESHIERBE"),("1047","QUEMANDO ALAMBRE"),
    ("1048","APOYO CAMPO EN GENERAL"),("1049","LOMBRICARIO"),
    ("1050","CORTINA APLICACION"),("1051","PREPARADOR DE MEZCLA"),
    ("1052","AUXILIAR PREPARADOR DE MEZCLAS"),("1053","CATERPILLAR"),
    ("1054","TRITURADORA DE BROCHA"),("1055","RETROESCABADORA"),
    ("1056","AMARRE DE PUENTES Y EXTENCIONES"),("1057","AUXILIAR OPERADOR"),
    ("1058","OPERADOR"),("1059","EMPAQUE CALABAZA"),("1060","EMPAQUE CALABAZA 1"),
    ("1061","LEVANTANDO CALABAZA"),("1062","MOVER CALABAZA"),
    ("1063","LIMPIEZA DE CUADROS"),("1064","APOYO GUARDERIA"),("1065","BATANGA 1"),
    ("1066","SERVICIO EN HACIENDA"),("1067","APOYO CAMPO ADMINISTRATIVO"),
    ("1068","VELADOR POZO"),("1069","VELADOR EMPAQUE"),("1070","VELADOR TALLER"),
    ("1071","VELADOR PORTERO"),("1072","GASTOS EMPAQUE CALABAZA"),("1074","TAXI"),
    ("1075","JONALERO TAXI"),("1076","REFORZAR Y PARCHAR AGRIBON"),
    ("1077","COLOCACION DE AROS"),("1078","ACARREO DE AROS Y AGRIBON"),
    ("1079","ALIMENTANDO LOMBRICES"),("1080","PLANTACION"),
    ("1081","INSTALACION PLASTICO Y CINTA"),("1082","PODA NOGAL SP + PLANTAS"),
    ("1083","RECEPCION FUNDACION"),("1084","COLOCACION DE AGRIBON"),
    ("1085","ENTRENE"),("1086","MONTACARGUISTA"),
    ("1087","MANTENIMIENTO DE EMPARRADO"),("1088","MARCACION PLANTACION"),
    ("1089","APLICACION MOCHOMO TOPOS"),("1090","DESBROTE"),("1091","MATEADO"),
    ("1092","ACOMODO DE GUIA"),("1093","ATOMIZANDO"),("1094","DESCOLE"),
    ("1095","SELECCION DE RACIMOS"),("1096","DESHOJE"),("1097","ANILLADA"),
    ("1098","DESPUNTE DE RACIMOS"),("1099","MONTACARGUISTA SANDIA"),
    ("1100","ETIQUETADOR SANDIA"),("1101","TARIMERO"),
    ("1102","LIMPIEZA EMPAQUE SANDIA"),("1103","APOYO EMPAQUE SANDIA"),
    ("1104","APUNTADOR COSECHA SANDIA"),("1105","GASTOS EMPAQUE SANDIA"),
    ("1106","TROQUE ACARREO DE SANDIA"),("1107","AUXILIAR ETIQUETADOR"),
    ("1108","BAÑERAS"),("1109","SELECCION Y DESPUNTE DE RACIMOS"),
    ("1110","TAPADO DE RACIMOS"),("1111","APOYO CAMPO RANCHO 1"),
    ("1112","RALEO POR DIA"),("1113","ARREGLO DE RACIMOS"),
    ("1114","ETIQUETADOR UVA"),("1115","CARGADOR UVA"),
    ("1116","AUXILIAR CARGADOR UVA"),("1117","APOYO INOCUIDAD"),
    ("1118","APOYO EMPAQUE UVA"),("1119","APOYO LIMPIEZA EMPAQUE UVA"),
    ("1120","PASERO"),("1121","SUPERVISOR UVA CAMPO"),
    ("1122","TROQUE ACARREO UVA"),("1123","ENCARGADA DE INOCUIDAD"),
    ("1124","CUADRILLERO TAXI"),("1125","APOYO CLINICA SALUD"),
    ("1126","APOYO RANCHO 3"),("1127","APOYO DENTISTA"),("1128","DESCHUPONE"),
    ("1129","INSTALACION DE EMPARRE"),("1130","DESEMPARRE"),
    ("1131","OPERADOR DUMPER"),("1132","APOYO CAMPERO PLANTA"),
    ("1133","CULTIVADORA"),("1134","APOYO CAMPO HERBICIDAS"),
    ("1135","BORDERO TRIPLE"),("1136","PASERO CUADRO"),
    ("1137","AUXILIAR MECANICO"),("1138","AUXILIAR TALLER"),
    ("1141","CUOTA TAXI"),("1142","REGADOR SP"),("1143","OPERADOR SP"),
    ("1144","VELADOR SP"),("1145","CUADRILLERO SP"),("1146","CUOTA TAXI SP"),
    ("1147","LIMPIEZA GENERAL SP"),("1148","PORTERO SP"),("1149","JORNAL SP"),
    ("1150","APOYO CAMPO GENERAL SP"),("1151","VELADOR CUADROS SP"),
    ("1152","AUXILIAR ALMACEN"),("1153","VIGILANTE SP"),("1154","COSECHA NUEZ"),
    ("1155","CARGADOR NUEZ SP"),("1156","OPERADOR COSECHA NUEZ SP"),
    ("1162","COSECHA NUEZ CUBETAS SP 50S"),("1164","CONTRATO SANDIA"),
    ("1165","CONTRATO UVA"),("1172","CORTAR CALABAZA"),
    ("1176","RIEGO RODADO"),("1178","CONTRATO PODA"),
    ("1180","PLANTACION"),("1182","PODA NOGAL SP"),("1183","PODA NOGAL AC"),
    ("1240","COSECHA UVA DIARIO"),("1290","CONTRATO RALEO"),
    ("1300","PODA NOGAL"),("1301","QUITAR PLASTICO-CINTA"),
    ("1302","SACAR GUIA"),("1330","CONTRATO DESBROCHE"),
    ("1389","PODA DIARIO 2023/2024"),("1391","ACARREO Y MOJADO DE PLANTA"),
    ("1395","TAREAS PLASTICO, CINTA Y AROS"),("1398","CORTA GUIAS"),
    ("1399","BORDERO INVERTIDO"),("1421","CONTEO DE RACIMOS"),
    ("1442","ARREGLO DE RACIMOS 1/4"),("1446","DESHIERBE"),
    ("1449","CONTAR PLANTAS"),("1456","PODA DIA 2024-2025"),
    ("1458","AMARRE DE PUENTES Y EXTENSIONES 2024"),("1462","POLINIZADOR"),
    ("1499","DESGALLE"),("1500","EMPAQUE GENERAL BICENTENARIO"),
    ("1503","DESHOJE 2 TARDEADA"),("1504","ACOMODO DE GUIA 2 TARDEADA"),
    ("1507","CALIDAD EMPAQUE"),("1508","ARMADO DE CAJA UVA"),
    ("1541","DESCABEZADO DE PLANTAS"),("1542","ENCARGADA DE LABORATORIO"),
]

# =============================================================================
#  CONSTANTES
# =============================================================================
ARCHIVO_DATOS      = "cuadrillero_data.json"
ARCHIVO_LISTA      = "lista_asistencia.json"
PUERTO_ANUNCIO     = 45678
PUERTO_VALIDACION  = 45679
PUERTO_CUADRILLERO = 45680
PUERTO_RECEPCION   = 45681
PUERTO_ANUNCIO_CU  = 45682   # Cuadrillero -> Apuntador (anuncio presencia)
INTERVALO_ANUNCIO  = 30      # segundos entre anuncios al apuntador


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
    PantallaBuscadorActividad:
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

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint: (0.96, None)
            height: '48dp'
            pos_hint: {'center_x': 0.5, 'top': 0.86}
            spacing: '8dp'

            MDTextField:
                id: input_cuadro
                hint_text: "Cuadro / Lote"
                line_color_focus: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.4

            MDRectangleFlatButton:
                id: btn_actividad
                text: root.actividad_seleccionada
                theme_text_color: "Custom"
                text_color: 0.18, 0.29, 0.12, 1
                line_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.6
                on_release: app.root.current = 'buscador'

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
                        text: root.estado_escucha
                        font_style: "Caption"
                        bold: True
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: root.color_estado_escucha
                    MDLabel:
                        text: "Estado WiFi"
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
                size_hint_x: 0.5
                elevation: 3
                on_release: root.validar_todos()

            MDRaisedButton:
                text: "VER RESUMEN"
                md_bg_color: 0.96, 0.65, 0.14, 1
                text_color: 0.18, 0.29, 0.12, 1
                size_hint_x: 0.5
                elevation: 3
                on_release: root.ver_resumen()

        MDRectangleFlatButton:
            text: "MI CREDENCIAL"
            theme_text_color: "Custom"
            text_color: 0.18, 0.29, 0.12, 1
            line_color: 0.18, 0.29, 0.12, 1
            size_hint: (0.96, 0.07)
            pos_hint: {'center_x': 0.5, 'y': 0.01}
            on_release: app.root.current = 'credencial'


<PantallaBuscadorActividad>:
    name: 'buscador'

    MDFloatLayout:
        md_bg_color: 0.96, 0.96, 0.94, 1

        MDFloatLayout:
            size_hint_y: 0.13
            pos_hint: {'x': 0, 'top': 1}
            md_bg_color: 0.18, 0.29, 0.12, 1

            MDLabel:
                text: "SELECCIONAR ACTIVIDAD"
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

        MDTextField:
            id: input_buscar
            hint_text: "Buscar actividad por nombre o clave..."
            line_color_focus: 0.18, 0.29, 0.12, 1
            pos_hint: {'center_x': 0.5, 'top': 0.85}
            size_hint: (0.96, None)
            height: '48dp'
            on_text: root.filtrar_actividades(self.text)

        ScrollView:
            size_hint: (0.96, 0.68)
            pos_hint: {'center_x': 0.5, 'top': 0.76}

            MDList:
                id: lista_actividades

        MDRectangleFlatButton:
            text: "CANCELAR"
            theme_text_color: "Custom"
            text_color: 0.72, 0.10, 0.10, 1
            line_color: 0.72, 0.10, 0.10, 1
            size_hint: (0.96, 0.07)
            pos_hint: {'center_x': 0.5, 'y': 0.01}
            on_release: app.root.current = 'asistencia'


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
                    height: '96dp'

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
        try:
            from plyer import filechooser as fc
            fc.open_file(
                title="Selecciona tu foto de perfil",
                filters=[("Imagenes", "*.jpg", "*.jpeg", "*.png")],
                on_selection=self.al_seleccionar_foto
            )
        except Exception as e:
            self.ids.label_foto.text = f"Error galeria: {e}"

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
        app = MDApp.get_running_app()
        pa  = app.root.get_screen('asistencia')
        pa.titulo_sesion = f"Cuadrilla {self.num_cuadrilla}"
        pa.fecha_hoy     = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
        app.iniciar_escucha_trabajadores()
        app.iniciar_respuesta_apuntador()
        app.iniciar_anuncio_apuntador()
        app.root.current = 'asistencia'
        Snackbar(text="Escuchando trabajadores...").open()


class PantallaAsistencia(Screen):
    titulo_sesion        = StringProperty("Cuadrilla")
    fecha_hoy            = StringProperty("")
    total_presentes      = StringProperty("0")
    total_detectados     = StringProperty("0")
    estado_escucha       = StringProperty("Inactivo")
    color_estado_escucha = ListProperty([0.6, 0.6, 0.6, 1])
    actividad_seleccionada = StringProperty("Seleccionar actividad...")

    def actualizar_lista_ui(self, trabajadores: dict):
        self.ids.lista_trabajadores.clear_widgets()
        presentes = 0
        for credencial, info in trabajadores.items():
            validado = info.get('validado', False)
            nombre   = info.get('nombre', f"Cred. {credencial}")
            hora     = info.get('hora_deteccion', '--:--')
            gps_txt  = info.get('gps', '')
            if validado:
                presentes += 1
            icono = IconLeftWidget(
                icon="check-circle" if validado else "wifi",
                theme_text_color="Custom",
                icon_color=(0.18, 0.29, 0.12, 1) if validado else (0.96, 0.65, 0.14, 1)
            )
            item = TwoLineIconListItem(
                text=f"[b]{nombre}[/b]  |  No. {credencial}",
                secondary_text=(
                    f"{hora}  |  {'VALIDADO' if validado else 'Pendiente'}"
                    + (f"  |  {gps_txt}" if gps_txt else "")
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
                app.enviar_validacion(cred)
                count += 1
        Snackbar(
            text=f"{count} trabajador(es) validados" if count
            else "Todos ya estan validados"
        ).open()

    def ver_resumen(self):
        app      = MDApp.get_running_app()
        cuadro   = self.ids.input_cuadro.text.strip().upper() or "SIN CUADRO"
        actividad = self.actividad_seleccionada
        pr       = app.root.get_screen('resumen')
        pr.construir_resumen(
            app.trabajadores_detectados,
            app.nombre_cuadrillero,
            app.num_cuadrilla,
            cuadro,
            actividad
        )
        app.cuadro_trabajo    = cuadro
        app.actividad_trabajo = actividad
        app.root.current      = 'resumen'


class PantallaBuscadorActividad(Screen):
    def on_enter(self):
        self.ids.input_buscar.text = ""
        self.filtrar_actividades("")

    def filtrar_actividades(self, texto):
        self.ids.lista_actividades.clear_widgets()
        txt = texto.strip().upper()
        resultados = [
            (clave, desc) for clave, desc in ACTIVIDADES
            if txt in desc.upper() or txt in clave
        ] if txt else ACTIVIDADES[:50]

        for clave, desc in resultados:
            item = OneLineListItem(
                text=f"{clave} - {desc}",
                on_release=lambda x, c=clave, d=desc: self._seleccionar(c, d)
            )
            self.ids.lista_actividades.add_widget(item)

    def _seleccionar(self, clave, desc):
        app = MDApp.get_running_app()
        pa  = app.root.get_screen('asistencia')
        pa.actividad_seleccionada = f"{clave} - {desc}"
        app.actividad_trabajo     = f"{clave} - {desc}"
        app.root.current          = 'asistencia'


class PantallaResumen(Screen):
    resumen_texto = StringProperty("")

    def construir_resumen(self, trabajadores, cuadrillero, cuadrilla, cuadro, actividad):
        presentes = sum(1 for v in trabajadores.values() if v.get('validado'))
        total     = len(trabajadores)
        fecha     = datetime.datetime.now().strftime("%d/%m/%Y")
        self.resumen_texto = (
            f"Cuadrilla {cuadrilla} | {cuadro}\n"
            f"Actividad: {actividad}\n"
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
            "actividad":    app.actividad_trabajo,
            "trabajadores": app.trabajadores_detectados
        }
        guardar_lista(datos)
        Snackbar(text="Lista guardada correctamente").open()


class CuadrilleroAgriCactusApp(MDApp):
    nombre_cuadrillero      = ""
    num_cuadrilla           = ""
    cuadro_trabajo          = ""
    actividad_trabajo       = ""
    trabajadores_detectados = {}
    _escucha_activa         = False
    _anuncio_activo         = False

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

    def iniciar_escucha_trabajadores(self):
        if self._escucha_activa:
            return
        self._escucha_activa = True

        pa = self.root.get_screen('asistencia')
        pa.estado_escucha       = "Activo"
        pa.color_estado_escucha = [0.18, 0.29, 0.12, 1]

        def _escuchar():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.bind(('', PUERTO_ANUNCIO))
                    sock.settimeout(2.0)

                    while self._escucha_activa:
                        try:
                            datos_raw, addr = sock.recvfrom(1024)
                            mensaje = datos_raw.decode('utf-8').strip()
                            partes  = mensaje.split(':')

                            # Formato: PRESENTE:<cred>:<cuadrilla>:<nombre>:<lat>:<lon>
                            if len(partes) >= 4 and partes[0] == 'PRESENTE':
                                credencial = partes[1]
                                cuadrilla  = partes[2]
                                nombre     = partes[3]
                                lat        = partes[4] if len(partes) > 4 else "0"
                                lon        = partes[5] if len(partes) > 5 else "0"

                                if cuadrilla != str(self.num_cuadrilla):
                                    continue

                                ahora  = datetime.datetime.now().strftime("%H:%M:%S")
                                ip     = addr[0]
                                gps_txt = f"{lat},{lon}" if lat != "0" else ""

                                if credencial not in self.trabajadores_detectados:
                                    self.trabajadores_detectados[credencial] = {
                                        "nombre":         nombre,
                                        "hora_deteccion": ahora,
                                        "validado":       False,
                                        "ip":             ip,
                                        "gps":            gps_txt
                                    }
                                else:
                                    self.trabajadores_detectados[credencial]["ip"]     = ip
                                    self.trabajadores_detectados[credencial]["nombre"] = nombre
                                    self.trabajadores_detectados[credencial]["gps"]    = gps_txt

                                Clock.schedule_once(lambda dt: self._actualizar_ui(), 0)

                        except socket.timeout:
                            continue
                        except Exception as e:
                            print(f"[WIFI] Error escucha: {e}")

            except Exception as e:
                print(f"[WIFI] Error servidor: {e}")
            finally:
                self._escucha_activa = False

        threading.Thread(target=_escuchar, daemon=True).start()

    def _actualizar_ui(self):
        pa = self.root.get_screen('asistencia')
        if self.root.current == 'asistencia':
            pa.actualizar_lista_ui(self.trabajadores_detectados)

    def enviar_validacion(self, credencial):
        info = self.trabajadores_detectados.get(credencial, {})
        ip   = info.get('ip')
        if not ip:
            Snackbar(text=f"Sin IP para cred. {credencial}").open()
            return

        fecha   = datetime.datetime.now().strftime("%Y-%m-%d")
        mensaje = f"VALIDAR:{credencial}:{self.num_cuadrilla}:{fecha}"

        def _enviar():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(3.0)
                    sock.sendto(mensaje.encode('utf-8'), (ip, PUERTO_VALIDACION))
                    try:
                        resp_raw, _ = sock.recvfrom(256)
                        resp = resp_raw.decode('utf-8').strip()
                        if resp.startswith(f"OK:{credencial}"):
                            Clock.schedule_once(
                                lambda dt: self._confirmar_validacion(credencial), 0
                            )
                    except socket.timeout:
                        Clock.schedule_once(
                            lambda dt: self._confirmar_validacion(credencial), 0
                        )
            except Exception as e:
                print(f"[WIFI] Error validacion: {e}")

        threading.Thread(target=_enviar, daemon=True).start()

    def _confirmar_validacion(self, credencial):
        if credencial in self.trabajadores_detectados:
            self.trabajadores_detectados[credencial]['validado']        = True
            self.trabajadores_detectados[credencial]['hora_validacion'] = \
                datetime.datetime.now().strftime("%H:%M:%S")
        self._actualizar_ui()
        Snackbar(text=f"Cred. {credencial} validado").open()

    # ── Anuncio al apuntador ──────────────────────────────────────────────────
    def iniciar_anuncio_apuntador(self):
        """
        Emite broadcast cada 30s para que el apuntador detecte este cuadrillero.
        Formato: CUADRILLERO:<cuadrilla>:<nombre>
        """
        if self._anuncio_activo:
            return
        self._anuncio_activo = True

        def _anunciar():
            import time
            while self._anuncio_activo:
                try:
                    nombre_limpio = str(self.nombre_cuadrillero).replace(':', ' ').replace('\n', ' ')
                    mensaje = f"CUADRILLERO:{self.num_cuadrilla}:{nombre_limpio}"
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                        sock.sendto(
                            mensaje.encode('utf-8'),
                            ('255.255.255.255', PUERTO_ANUNCIO_CU)
                        )
                    print(f"[WIFI] Anuncio apuntador: {mensaje}")
                except Exception as e:
                    print(f"[WIFI] Error anuncio apuntador: {e}")
                time.sleep(INTERVALO_ANUNCIO)

        threading.Thread(target=_anunciar, daemon=True).start()

    # ── Responder al apuntador (peticion de lista) ────────────────────────────
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
                            print(f"[WIFI] Error apuntador: {e}")
            except Exception as e:
                print(f"[WIFI] Error servidor apuntador: {e}")

        threading.Thread(target=_escuchar, daemon=True).start()

    def _enviar_lista_apuntador(self, sock, addr):
        payload = {
            "tipo":         "LISTA_CUADRILLA",
            "cuadrilla":    self.num_cuadrilla,
            "cuadrillero":  self.nombre_cuadrillero,
            "cuadro":       self.cuadro_trabajo,
            "actividad":    self.actividad_trabajo,
            "fecha":        datetime.datetime.now().strftime("%Y-%m-%d"),
            "trabajadores": self.trabajadores_detectados
        }
        try:
            datos = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            sock.sendto(datos, (addr[0], PUERTO_RECEPCION))
            Snackbar(text="Lista enviada al apuntador").open()
        except Exception as e:
            print(f"[WIFI] Error enviando lista: {e}")

    def on_stop(self):
        self._escucha_activa = False
        self._anuncio_activo = False


if __name__ == '__main__':
    CuadrilleroAgriCactusApp().run()
