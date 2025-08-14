from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from ..models import Boleto

def enviar_boleto_por_email(boleto_id, request):
    try:
        boleto = Boleto.objects.get(id=boleto_id)
        reserva = boleto.reserva
        usuario = reserva.usuario_reserva
        
        # 1. Generar el contenido del PDF del boleto
        context = {'boleto': boleto, 'reserva': reserva}
        html_string = render_to_string('cliente/boleto_pdf.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_content = html.write_pdf()

        # 2. Preparar el contenido del email usando un template HTML
        asunto = f"Tu Boleto de Vuelo - Reserva #{reserva.codigo_reserva}"
        mensaje_html = render_to_string('cliente/boleto_email.html', {'reserva': reserva, 'boleto': boleto})

        # 3. Crear y enviar el email con el archivo adjunto
        email = EmailMessage(
            asunto,
            mensaje_html,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email]
        )
        email.content_subtype = "html"
        email.attach(f"Boleto-{boleto.codigo_barra}.pdf", pdf_content, 'application/pdf')
        email.send()

        return True, "Email enviado correctamente."

    except Boleto.DoesNotExist:
        return False, "El boleto no existe."
    except Exception as e:
        return False, f"Ocurrió un error al enviar el email: {str(e)}"