
import os
import requests
import smtplib

from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

def obtener_clima(ciudad, api_key):
    """Obtiene la temperatura y la descripción del clima."""

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={ciudad}&appid={api_key}&lang=es&units=metric"
    )

    try:
        respuesta = requests.get(url, timeout=10)

        if respuesta.status_code == 200:
            datos = respuesta.json()

            temperatura = datos["main"]["temp"]
            descripcion = datos["weather"][0]["description"]

            return temperatura, descripcion

        else:
            print(
                "Error al obtener el clima. "
                f"Código de estado: {respuesta.status_code}"
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None

    except (KeyError, IndexError, ValueError) as e:
        print(f"Error al procesar los datos del clima: {e}")
        return None


def enviar_email(remitente, password, destinatario, asunto, contenido):
    """Envía un correo electrónico mediante el servidor SMTP de Gmail."""

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto

    # Agregar el contenido en texto plano con codificación UTF-8
    mensaje.attach(MIMEText(contenido, "plain", "utf-8"))

    try:
        # Conectarse al servidor de Gmail en el puerto 587
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(remitente, password)

            server.sendmail(
                remitente,
                destinatario,
                mensaje.as_string()
            )

        print("Correo enviado exitosamente.")

    except (smtplib.SMTPException, OSError) as e:
        print(f"Error al enviar el correo: {e}")


if __name__ == "__main__":

    # Leer las variables desde el archivo .env
    API_KEY = os.getenv("API_KEY")
    CIUDAD = os.getenv("CIUDAD")
    CORREO_REMITENTE = os.getenv("CORREO_REMITENTE")
    CONTRASENA = os.getenv("CONTRASENA")
    CORREO_DESTINATARIO = os.getenv("CORREO_DESTINATARIO")

    # Comprobar que todas las variables estén configuradas
    variables = [
        ("API_KEY", API_KEY),
        ("CIUDAD", CIUDAD),
        ("CORREO_REMITENTE", CORREO_REMITENTE),
        ("CONTRASENA", CONTRASENA),
        ("CORREO_DESTINATARIO", CORREO_DESTINATARIO),
    ]

    missing = [nombre for nombre, valor in variables if not valor]

    if missing:
        print(
            "Faltan variables de entorno: "
            + ", ".join(missing)
        )

    else:
        # Obtener la información del clima
        resultado_clima = obtener_clima(CIUDAD, API_KEY)

        if resultado_clima:
            temperatura, descripcion = resultado_clima

            print(f"Ciudad: {CIUDAD}")
            print(f"Temperatura: {temperatura} °C")
            print(f"Descripción: {descripcion}")

            # Preparar el contenido del correo
            asunto = f"Reporte del clima en {CIUDAD}"

            contenido = (
                f"Reporte del clima\n\n"
                f"Ciudad: {CIUDAD}\n"
                f"Temperatura: {temperatura} °C\n"
                f"Descripción: {descripcion.capitalize()}\n\n"
                f"Este reporte fue generado automáticamente.\n\n"
                f"Saludos,\n"
                f"Sistema de Automatizacion de Correos Combarranquilla\n"
                f"Remitente: {CORREO_REMITENTE}\n"
            )

            # Enviar el correo electrónico
            enviar_email(
                CORREO_REMITENTE,
                CONTRASENA,
                CORREO_DESTINATARIO,
                asunto,
                contenido
            )
        else:
            print("No se pudo obtener la información del clima.")