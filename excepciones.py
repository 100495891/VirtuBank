class ArchivoNoEncontradoError(FileNotFoundError):
    """Excepción para archivo no encontrado."""
    pass

class ClaveNoEncontradaError(KeyError):
    """Excepción para clave no encontrada en un diccionario."""
    pass

class ValorInvalidoError(ValueError):
    """Excepción para valores inválidos."""
    pass

class ClaveInvalidaError(Exception):
    """Excepción para claves criptográficas inválidas."""
    pass

class OperacionInvalidaError(Exception):
    """Excepción para operaciones no válidas."""
    pass
class UsuarioNoRegistradoError(Exception):
    """Excepción para usuarios no registrados en Bizum."""
    pass

class ErrorCertificadoError(Exception):
    """Excepción para errores relacionados con certificados."""
    pass
class ErrorEliminarCuentaError(Exception):
    """Excepción para errores al intentar eliminar la cuenta del usuario."""
    pass
class ErrorCifradoError(Exception):
    """Excepción para errores relacionados con el cifrado o descifrado de datos."""
    pass
class ErrorGenerarClaveError(Exception):
    """Excepción para errores en la generación de la clave privada."""
    pass

class ErrorFirmaError(Exception):
    """Excepción para errores al firmar mensajes."""
    pass

class ErrorVerificarFirmaError(Exception):
    """Excepción para errores al verificar la firma."""
    pass

class ErrorCSRGenerationError(Exception):
    """Excepción para errores en la generación del CSR (Solicitud de Firma de Certificado)."""
    pass

class ErrorRegistroUsuarioError(Exception):
    """Excepción para errores en el registro de usuario."""
    pass

class ErrorLoginUsuarioError(Exception):
    """Excepción para errores en el inicio de sesión de usuario."""
    pass