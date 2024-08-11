import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ecommerce import app, db 


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run()
