from asistente.core import AsistenteVirtual
from asistente.voz import Voz
from asistente.buscador import Buscador

# Cambia aquí el modelo según el entorno
from asistente.ia.tiny_model import TinyModel
from asistente.ia.big_model import BigModel
from asistente.ia.webui_model import WebUIModel

# Cambia aquí el modelo por defecto
modelo_ia = TinyModel()  # O BigModel() o WebUIModel()
# Prueba de modelo


def main():
    voz = Voz()
    buscador = Buscador()
    modelo_ia = TinyModel()

    servicios = {
        'buscador': buscador,
        'modelo_ia': modelo_ia,
    }

    asistente = AsistenteVirtual(voz, servicios)

    voz.hablar("Estoy en espera. Di 'activar asistente' para comenzar o 'salir' para cancelar.")

    while True:
        resultado = voz.escuchar_para_activar()

        if resultado == "activar asistente":
            voz.hablar("Activando asistente.")
            asistente.iniciar()
            break

        elif resultado in ("salir", "cancelar"):
            voz.hablar("Saliendo. Hasta luego.")
            break

        elif resultado:
            voz.hablar("Aún no estoy activado. Di 'activar asistente' si quieres empezar.")

if __name__ == "__main__":
    main()