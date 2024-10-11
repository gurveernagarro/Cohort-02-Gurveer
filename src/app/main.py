import sys
import os

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from app.api.endpoints import view

app = FastAPI()


app.include_router(view.router)
