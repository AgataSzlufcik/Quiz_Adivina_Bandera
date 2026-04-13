# 🌍 Adivina el País

Quiz interactivo de geografía construido con Python y Streamlit.

El juego muestra la bandera de un país y el jugador debe identificarlo 
entre 4 opciones. Puede comprar pistas (capital, continente, población, idioma) 
a cambio de puntos, lo que añade una capa de estrategia.

Al finalizar las 20 rondas se muestra un score de eficiencia que mide 
cuántos puntos se gastaron en pistas frente al total posible.

## Tecnologías

- Python + Streamlit (interfaz web interactiva)
- REST Countries API (datos en tiempo real de 180+ países)
- Pandas (limpieza y manipulación de datos)

## Cómo ejecutar

git clone https://github.com/AgataSzlufcik/Quiz_Adivina_Bandera.gitgit add README.md

cd mi-proyecto
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Funcionalidades

- 180+ países obtenidos en tiempo real desde una API REST
- Sistema de pistas de pago (cada pista cuesta 1 punto)
- Puntuación y score de eficiencia al finalizar
- 20 preguntas por partida con países aleatorios

👤 Autor

Agata con ayuda de Claude