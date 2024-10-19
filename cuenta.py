import random

def generar_codigo_entidad():
    """Genera un código de entidad aleatorio (4 dígitos)."""
    return ''.join(random.choices('0123456789', k=4))

def generar_codigo_oficina():
    """Genera un código de oficina aleatorio (4 dígitos)."""
    return ''.join(random.choices('0123456789', k=4))

def generar_numero_cuenta():
    """Genera un número de cuenta bancaria aleatorio en formato IBAN español."""
    entidad = generar_codigo_entidad()
    oficina = generar_codigo_oficina()
    cuenta = ''.join(random.choices('0123456789', k=10))  # 10 dígitos para el número de cuenta

    # Generar dígitos de control (kk) - en un entorno real, esto se calcularía correctamente
    # Para simplificar, se pueden generar aleatoriamente.
    digitos_control = ''.join(random.choices('0123456789', k=2))

    # Formato IBAN
    iban = f"ES{digitos_control} {entidad} {oficina} {cuenta}"
    return iban


def calcular_digito_control(numero):
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
    return (10 - (suma % 10)) % 10


def generar_numero_tarjeta_visa():
    """Genera un número de tarjeta Visa válido."""
    iin = '4' + ''.join(random.choices('0123456789', k=5))  # 6 dígitos, comenzando con 4
    cuenta = ''.join(random.choices('0123456789', k=9))  # 9 dígitos para el número de cuenta
    numero_sin_control = iin + cuenta
    digito_control = calcular_digito_control(numero_sin_control)
    numero_tarjeta = numero_sin_control + str(digito_control)

    return numero_tarjeta