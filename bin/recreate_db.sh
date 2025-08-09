#!/bin/sh

python -c "from backend.src.db import db;
from backend.src.app import app;
with app.app_context():
  db.drop_all();
  db.create_all()"
