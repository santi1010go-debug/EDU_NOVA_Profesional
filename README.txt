EDU NOVA — PROYECTO PROFESIONAL

REQUISITOS
- Python 3.10 o superior
- Flask
- Werkzeug (se instala como dependencia de Flask)

INSTALACIÓN
1. Descomprime la carpeta.
2. Abre una terminal dentro de la carpeta EDU_NOVA_Profesional.
3. Instala Flask:
   python -m pip install flask
4. Ejecuta:
   python app.py
5. Abre en el navegador:
   http://127.0.0.1:5000/

ESTRUCTURA
app.py
templates/
  base.html
  index.html
  login.html
  registro.html
  dashboard.html
  matematicas.html
  lengua.html
  juegos.html
  videos.html
  examen.html
  404.html
static/
  css/estilos.css
  js/script.js

NOTAS
- La base de datos usuarios.db se crea automáticamente al ejecutar app.py.
- Crea una cuenta desde “Crear cuenta” antes de iniciar sesión.
- Las páginas de aprendizaje requieren iniciar sesión.
- Los juegos incluyen preguntas funcionales y guardan el resultado en SQLite.
- Cambia app.secret_key antes de publicar la app en internet.
