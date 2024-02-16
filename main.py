import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()

@app.post("/")
async def hello():
    return {"Welcome": "The API is online!}
    
@app.post("/area")
async def area(image_path: str):
    try:
        # Leitura da imagem do arquivo carregado
        resposta = requests.get(image_path)
        conteudo_imagem = resposta.content
        imagem_np = np.frombuffer(conteudo_imagem, np.uint8)
        image = cv2.imdecode(imagem_np, cv2.IMREAD_COLOR)
        #image = cv2.imdecode(np.fromstring(await file.read(), np.uint8), cv2.IMREAD_COLOR)

        # Conversão de BGR para HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Definição da faixa de cor verde em HSV
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([70, 255, 255])

        # Limiar da imagem HSV para obter apenas cores verdes
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        # Encontrar contornos na máscara verde
        contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Cálculo da área do quadrado verde (assumido como 1 cm²) em pixels
        green_area_pixels = 0
        for cnt in contours:
            green_area_pixels += cv2.contourArea(cnt)

        # Cálculo da escala do quadrado verde em cm²
        green_scale_cm2 = 1.0 / green_area_pixels

        # Definição da faixa de cor vermelha em HSV
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])

        # Limiar da imagem HSV para obter apenas cores vermelhas
        mask_red = cv2.inRange(hsv, lower_red, upper_red)

        # Encontrar contornos na máscara vermelha
        contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Cálculo da área do objeto vermelho (ferida) em pixels
        red_area_pixels = 0
        for cnt in contours:
            red_area_pixels += cv2.contourArea(cnt)

        # Conversão da área vermelha de pixels para cm² usando a escala do quadrado verde
        red_area_cm2 = red_area_pixels * green_scale_cm2

        return {"area": red_area_cm2}

    except Exception as e:
        return {"error": str(e)}

