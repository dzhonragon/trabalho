"""Ponto de entrada simples para execução local."""
from mercadinho import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
