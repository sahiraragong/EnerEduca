from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import SensorData
from django.utils.timezone import is_aware
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.conf import settings

# ⚙️ Umbral de temperatura crítica
UMBRAL_TEMPERATURA = 60.0  # °C

# 🚨 Botón de emergencia
def emergencia(request):
    ultima = SensorData.objects.last()
    if ultima:
        # Enviar correo de alerta
        send_mail(
            subject="⚠️ Alerta de Temperatura Crítica",
            message=f"Se detectó una temperatura de {ultima.temperatura}°C el {ultima.fecha_hora}. "
                    "Por favor revise el sistema inmediatamente.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["sahiraragongomez50@gmail.com"],  # Cambia por tu correo real
            fail_silently=False,
        )
    return redirect('dashboard')


# 📊 DASHBOARD: mostrar último registro
def dashboard(request):
    ultima = SensorData.objects.last()
    if ultima and ultima.temperatura >= UMBRAL_TEMPERATURA:
        # Enviar alerta automáticamente
        send_mail(
            subject="🔥 Alerta Automática: Temperatura Crítica",
            message=(
                f"Se detectó una temperatura crítica de {ultima.temperatura}°C "
                f"registrada el {ultima.fecha_hora}. "
                "Por favor, revise el sistema inmediatamente."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["sahiraragongomez50@gmail.com"],  # cambia por tu correo
            fail_silently=True,
        )
    return render(request, 'energymonitor/dashboard.html', {
        'ultima': ultima,
        'UMBRAL_TEMPERATURA': UMBRAL_TEMPERATURA
    })


# 📩 API: recibir datos desde la ESP32
@csrf_exempt
def recibir_dato(request):
    if request.method in ['POST', 'GET']:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.method == 'POST' else request.GET
        except:
            data = request.POST

        temperatura = data.get('temperatura')
        humedad = data.get('humedad')
        voltaje = data.get('voltaje')
        corriente = data.get('corriente')
        potencia = data.get('potencia')
        energia = data.get('energia')
        frecuencia = data.get('frecuencia')
        factor_potencia = data.get('factor_potencia')

        if temperatura is None or humedad is None:
            return JsonResponse({'estado': 'error', 'msg': 'Faltan datos de temperatura o humedad'}, status=400)

        try:
            SensorData.objects.create(
                temperatura=float(temperatura),
                humedad=float(humedad),
                voltaje=float(voltaje) if voltaje else 0.0,
                corriente=float(corriente) if corriente else 0.0,
                potencia=float(potencia) if potencia else 0.0,
                energia=float(energia) if energia else 0.0,
                frecuencia=float(frecuencia) if frecuencia else 0.0,
                factor_potencia=float(factor_potencia) if factor_potencia else 0.0
            )

            # ⚠️ Si la temperatura excede el umbral, enviar correo automático
            if float(temperatura) >= UMBRAL_TEMPERATURA:
                send_mail(
                    subject="🔥 Temperatura Crítica Detectada",
                    message=f"Temperatura de {temperatura}°C detectada. Revisar el sistema urgentemente.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["mantenimiento@empresa.com"],
                    fail_silently=True,
                )

            return JsonResponse({'estado': 'ok', 'msg': 'Datos guardados correctamente'})
        except Exception as e:
            return JsonResponse({'estado': 'error', 'msg': str(e)}, status=500)

    return JsonResponse({'estado': 'error', 'msg': 'Método no permitido'}, status=405)


# 📜 HISTORIAL
def historial(request):
    datos = SensorData.objects.order_by('-fecha_hora')[:50]
    return render(request, 'energymonitor/historial.html', {'datos': datos})


# 📤 EXPORTAR A EXCEL
def exportar_excel(request):
    datos = SensorData.objects.all().values()
    df = pd.DataFrame(datos)
    if 'fecha_hora' in df.columns:
        df['fecha_hora'] = df['fecha_hora'].apply(lambda x: x.replace(tzinfo=None) if is_aware(x) else x)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=mediciones.xlsx'
    df.to_excel(response, index=False)
    return response


# 📈 GRÁFICAS
def graficas(request):
    datos = SensorData.objects.order_by('-fecha_hora')[:30][::-1]
    etiquetas = [d.fecha_hora.strftime("%H:%M:%S") for d in datos]

    temperaturas = [d.temperatura for d in datos]
    humedades = [d.humedad for d in datos]
    voltajes = [d.voltaje for d in datos]
    corrientes = [d.corriente for d in datos]
    potencias = [d.potencia for d in datos]
    energias = [d.energia for d in datos]
    frecuencias = [d.frecuencia for d in datos]
    factores = [d.factor_potencia for d in datos]

    def generar_grafica(x, y_datos, etiquetas_y, titulo):
        fig, ax = plt.subplots()
        for y, label, marker in y_datos:
            ax.plot(x, y, label=label, marker=marker)
        ax.set_title(titulo)
        ax.set_xlabel('Hora')
        ax.set_ylabel('Valor')
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        return grafico

    graf1 = generar_grafica(etiquetas, [
        (temperaturas, "Temperatura (°C)", 'o'),
        (humedades, "Humedad (%)", 's')
    ], ['°C', '%'], 'Temperatura y Humedad')

    graf2 = generar_grafica(etiquetas, [
        (voltajes, "Voltaje (V)", 'o'),
        (corrientes, "Corriente (A)", 's'),
        (potencias, "Potencia (W)", '^')
    ], ['V', 'A', 'W'], 'Voltaje, Corriente y Potencia')

    graf3 = generar_grafica(etiquetas, [
        (energias, "Energía (kWh)", 'o'),
        (frecuencias, "Frecuencia (Hz)", 's'),
        (factores, "Factor Potencia", '^')
    ], ['kWh', 'Hz', ''], 'Energía, Frecuencia y Factor de Potencia')

    return render(request, 'energymonitor/graficas.html', {
        'graf1': graf1,
        'graf2': graf2,
        'graf3': graf3
    })


# 🧹 LIMPIAR DATOS
def limpiar_datos(request):
    SensorData.objects.all().delete()
    return redirect('historial')
