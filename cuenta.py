import random
from datetime import datetime, timedelta

class CuentaBancaria:
    def generar_numero_cuenta(self):
        """Genera un número de cuenta bancaria aleatorio en formato IBAN español."""
        entidad = ''.join(random.choices('0123456789', k=4))
        oficina = ''.join(random.choices('0123456789', k=4))
        cuenta = ''.join(random.choices('0123456789', k=10))  # 10 dígitos para el número de cuenta
        digitos_control = ''.join(random.choices('0123456789', k=2))

        # Formato IBAN
        iban = f"ES{digitos_control} {entidad} {oficina} {cuenta}"
        return iban


    def calcular_digito_control(self, numero):
        """Calcula el dígito de control usando el algoritmo de Luhn."""
        num_str = str(numero)
        suma = 0
        alt = False
        for i in range(len(num_str) - 1, -1, -1):
            n = int(num_str[i])
            if alt:
                n *= 2
                if n > 9:
                    n -= 9
            suma += n
            alt = not alt
        return str((10 - (suma % 10)) % 10)


    def generar_numero_tarjeta_visa(self):
        """Genera un número de tarjeta Visa válido."""
        iin = '4' + ''.join(random.choices('0123456789', k=5))  # 6 dígitos, comenzando con 4
        cuenta = ''.join(random.choices('0123456789', k=9))  # 9 dígitos para el número de cuenta
        numero_sin_control = iin + cuenta
        digito_control = self.calcular_digito_control(numero_sin_control)
        numero_tarjeta = f"{numero_sin_control}{digito_control}"

        return numero_tarjeta

    def generar_fecha_expiracion(self):
        fecha_actual = datetime.now()
        fecha_expiracion = fecha_actual + timedelta(days=5*365)
        mes = fecha_expiracion.month
        anio = fecha_expiracion.year % 100
        return f"{mes:02d}/{anio:02d}"