#!/bin/sh

python -c "from backend.src.db import db;
from backend.src.app import app;
with app.app_context():
  db.create_all()"
