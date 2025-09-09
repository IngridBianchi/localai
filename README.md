// Activar entorno virtual
source /home/alejandro/Escritorio/INGRID/Proyectos/localai/.venv/bin/activate

// Desactivar el entorno virtual
deactivate

// Instalar dependencias
/home/alejandro/Escritorio/INGRID/Proyectos/localai/.venv/bin/pip install -r requirements.txt

//Ejecutar scrip para limpieza de logs
python rotate_log.py
