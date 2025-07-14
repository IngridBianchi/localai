// Activar entorno virtual en cada terminal
source ~/Escritorio/INGRID/Proyectos/localai/venv/bin/activate

//Comandos git
git init
git add .
git commit -m "Primer commit del proyecto LocalAI"
git branch -M dev
git remote add origin https://github.com/IngridBianchi/localai.git
git push -u origin dev

//Esto reinicia la shell.
exec bash
