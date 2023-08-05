"""
Este módulo contém as funções comuns dos métodos de diferenças finitas
para equações diferenciais parciais.
"""

import sys

__all__ = ['check_method']


def check_method(method, methods):
    """Verifica se o método numérico 'method' é válido."""
    if method not in methods:
        sys.exit('Value \'' + method + '\' for argument \'method\' is not valid.')
