# Taller 4 — Despliegue en AWS EC2

Instancia: Amazon Linux 2023, t2.micro, sin key pair, HTTP y HTTPS habilitados.
Conexión: EC2 Instance Connect.

## 1. Dependencias del sistema

```bash
sudo dnf install python3.11 python3.11-pip git -y
```

## 2. Código del proyecto

```bash
git clone https://github.com/Pacha-e/Workshop-P1.git
cd Workshop-P1
sudo python3.11 -m pip install -r requirements.txt
```

La base de datos `db.sqlite3` ya incluye las descripciones del CSV y los embeddings
de las películas, así que no hay que regenerarlos en la instancia.

## 3. Clave de IA (solo para la página de recomendaciones)

La clave nunca se sube a GitHub. Se crea el archivo en la instancia:

```bash
cat > openAI.env <<'ENV'
AI_PROVIDER=gemini
gemini_apikey=PEGAR_AQUI_LA_CLAVE
ENV
```

## 4. Servidor

```bash
sudo python3.11 manage.py runserver 0.0.0.0:80
```

Abrir `http://<IP pública de la instancia>/recommendations/` en el navegador.

## 5. Al terminar

`Ctrl+C`, luego en EC2: Estado de la instancia → Detener instancia, y en el Learner Lab: End Lab.
