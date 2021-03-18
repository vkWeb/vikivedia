import os

with open(".env", "w") as envfile:
    envfile.write(f"SECRET_KEY={os.urandom(64)}\n")
