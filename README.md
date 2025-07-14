// Activar entorno virtual en cada terminal
source ~/Escritorio/INGRID/Proyectos/localai/venv/bin/activate

git init
git add .
git commit -m "Primer commit del proyecto LocalAI"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/localai-docker.git
git push -u origin main

Esto reinicia la shell.
exec bash
