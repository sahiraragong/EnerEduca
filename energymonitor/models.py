from django.db import models
from django.utils import timezone

class SensorData(models.Model):
    temperatura = models.FloatField(default=0.0)
    humedad = models.FloatField(default=0.0)
    voltaje = models.FloatField(default=0.0)
    corriente = models.FloatField(default=0.0)
    potencia = models.FloatField(default=0.0)
    energia = models.FloatField(default=0.0)  # en kWh
    frecuencia = models.FloatField(default=0.0)
    factor_potencia = models.FloatField(default=0.0)
    fecha_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"T: {self.temperatura:.1f}°C, H: {self.humedad:.1f}%, "
            f"V: {self.voltaje:.1f}V, A: {self.corriente:.2f}A, "
            f"P: {self.potencia:.1f}W, E: {self.energia:.3f}kWh, "
            f"Hz: {self.frecuencia:.1f}, FP: {self.factor_potencia:.2f}"
        )
