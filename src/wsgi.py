import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# print(sys.path)

import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug(sys.path)

from ecommerce import app, db 


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run()
