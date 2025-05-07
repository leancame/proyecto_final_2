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
    modelo_ia = TinyModel()  # Cambiar por TinyModel() o BigModel()

    servicios = {
        'buscador': buscador,
        'modelo_ia': modelo_ia,
    }

    asistente = AsistenteVirtual(voz, servicios)
    asistente.iniciar()

if __name__ == "__main__":
    main()

