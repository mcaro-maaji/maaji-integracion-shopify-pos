"""TODO: DOCS"""

from .cli import cli
from .utils import load_dotenv, CURRENT_WORKING_DIR

def main():
    """Función principal que ejecuta el cli."""
    load_dotenv()
    load_dotenv(CURRENT_WORKING_DIR / ".env") # Test

    cli()

if __name__ == "__main__":
    main()
