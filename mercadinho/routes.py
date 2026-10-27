"""Carrega rotas de autenticação e produtos no blueprint principal."""
from .views import bp  # noqa: F401
from . import auth as _auth  # noqa: F401,E402
from . import products as _products  # noqa: F401,E402
