"""
Utilidades para validación de entradas y seguridad
"""


def validar_nombre_canal(canal: str) -> None:
    """
    Valida que el nombre del canal no contenga caracteres peligrosos.

    Args:
        canal: Nombre del canal a validar

    Raises:
        ValueError: Si el canal contiene caracteres inválidos
    """
    if not canal or not isinstance(canal, str):
        raise ValueError("Canal inválido")

    # Prevenir path traversal
    if '..' in canal or '/' in canal or '\\' in canal:
        raise ValueError(f"Canal contiene caracteres inválidos: {canal}")


def validar_nombre_archivo(archivo: str, extension: str = '.ts') -> None:
    """
    Valida que el nombre del archivo no contenga caracteres peligrosos.

    Args:
        archivo: Nombre del archivo a validar
        extension: Extensión esperada del archivo (por defecto .ts)

    Raises:
        ValueError: Si el archivo contiene caracteres inválidos
    """
    if not archivo or not isinstance(archivo, str):
        raise ValueError("Nombre de archivo inválido")

    # Prevenir path traversal
    if '..' in archivo or '/' in archivo or '\\' in archivo:
        raise ValueError(f"Nombre de archivo contiene caracteres inválidos: {archivo}")

    # Verificar extensión
    if extension and not archivo.endswith(extension):
        raise ValueError(f"El archivo debe terminar en {extension}: {archivo}")


def sanitizar_texto(texto: str, max_length: int = 200) -> str:
    """
    Sanitiza texto de entrada para búsquedas.

    Args:
        texto: Texto a sanitizar
        max_length: Longitud máxima permitida

    Returns:
        Texto sanitizado (sin espacios al inicio/fin)

    Raises:
        ValueError: Si el texto está vacío o excede la longitud máxima
    """
    if not texto or not isinstance(texto, str):
        raise ValueError("Texto inválido")

    texto_limpio = texto.strip()

    if not texto_limpio:
        raise ValueError("El texto no puede estar vacío")

    if len(texto_limpio) > max_length:
        raise ValueError(f"El texto excede la longitud máxima de {max_length} caracteres")

    return texto_limpio
