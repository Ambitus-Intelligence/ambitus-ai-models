import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cli import main

if __name__ == "__main__":
    main()