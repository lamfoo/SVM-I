import cv2
import re
import easyocr
import numpy as np
import requests
from loguru import logger

class PlateDataAnalysis:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['en'], gpu=False)  # Inicializa o EasyOCR para leitura de placas
        self.api_url = "http://127.0.0.1:8000/api/v1/inspections/"  # URL da API

    def is_valid_plate(self, plate: str) -> bool:
        """
        Verifica se a placa segue um dos padrões válidos.
        """
        # Padrões de matrícula válidos
        patterns = [
            r"^[A-Z]{3}[0-9]{3}[A-Z]{2}$",  # Exemplo: ABC123XY
            r"^[A-Z]{3}[0-9]{4}[A-Z]{2}$"   # Exemplo: ABC1234XY
        ]
        return any(re.fullmatch(pattern, plate) for pattern in patterns)

    def preprocess_image(self, path_image: str) -> np.ndarray:
        """
        Processa a imagem para facilitar a leitura da matrícula.
        """
        # Carrega a imagem
        image = cv2.imread(path_image, cv2.IMREAD_COLOR)
        if image is None:
            logger.error(f"Erro ao carregar a imagem: {path_image}")
            return None

        # Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Equalização adaptativa de histograma para melhorar contraste (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Ajuste de brilho e contraste
        alpha = 1.5  # Fator de contraste
        beta = 20    # Fator de brilho
        adjusted = cv2.convertScaleAbs(enhanced, alpha=alpha, beta=beta)

        # Aplica o desfoque Gaussiano para reduzir ruídos
        blurred = cv2.GaussianBlur(adjusted, (5, 5), 0)

        # Aplica threshold adaptativo para segmentação
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        return binary

    def read_text_from_image(self, processed_image: np.ndarray, decoder: str) -> list:
        """
        Lê o texto da imagem usando EasyOCR.
        """
        if processed_image is None:
            logger.error("Imagem processada inválida")
            return []

        try:
            results = self.reader.readtext(processed_image, decoder=decoder)
            return results
        except Exception as e:
            logger.error(f"Erro ao processar a imagem: {e}")
            return []

    def filter_plates(self, text_items: list) -> dict:
        """
        Filtra as matrículas extraídas com base na precisão e formato.
        """
        concatenated_text = ""  # String para armazenar o texto concatenado

        for item in text_items:
            # Extraímos o texto e removemos caracteres indesejados
            text = item[1].replace('-', '').replace(' ', '').replace('@', '').upper()  # Limpeza
            precision = item[2]  # A precisão da detecção

            logger.info(f'Texto extraído: "{text}", precisão: {precision}')

            # Adiciona o texto ao resultado concatenado
            concatenated_text += text

        # Verifica se o texto concatenado forma uma placa válida
        if self.is_valid_plate(concatenated_text):
            logger.info(f'Placa detectada: {concatenated_text}')
            api_response = self.consultar_api(concatenated_text)
            if api_response:
                return {"plate": concatenated_text, "precision": "N/A", "api_data": api_response}
            else:
                logger.error("Erro ao consultar a API.")
                return {"plate": concatenated_text, "precision": "N/A", "api_data": None}

        logger.info("Nenhuma placa válida foi detectada.")
        return None

    def consultar_api(self, plate: str) -> dict:
        """
        Consulta a API usando a matrícula detectada.
        """
        try:
            # Construa a URL com o parâmetro da matrícula extraída
            url = f"{self.api_url}?eq(matricula,'{plate}')"
            logger.info(f"Consultando API com a URL: {url}")

            # Realiza a consulta HTTP GET
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()  # Retorna os dados da API em formato JSON
            else:
                logger.error(f"Erro na consulta à API: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Erro ao consultar a API: {e}")
            return None
