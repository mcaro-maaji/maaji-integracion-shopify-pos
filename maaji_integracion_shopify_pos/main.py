"""TODO: DOCS"""

from .cli import cli
from .utils import load_dotenv, CURRENT_WORKING_DIR

load_dotenv()
load_dotenv(CURRENT_WORKING_DIR / ".env") # Test

def main():
    """Función principal que ejecuta el cli."""
    cli()

if __name__ == "__main__":
    main()
