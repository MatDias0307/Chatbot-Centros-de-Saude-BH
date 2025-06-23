from flask import Flask, request, jsonify
from flask_cors import CORS
from nlp.processor import NLPProcessor
import logging
from functools import wraps
from typing import Dict, Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://127.0.0.1:5500",
            "https://matdias0307.github.io/Chatbot-Centros-de-Saude-BH/"
        ]
    }
})

try:
    nlp_processor = NLPProcessor('data/centros_saude.csv')
    logger.info("NLPProcessor inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar NLPProcessor: {str(e)}")
    raise

def validate_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("Requisição inválida - campo 'message' ausente")
            return jsonify({'error': 'Requisição inválida. Esperado campo "message".'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            logger.warning("Mensagem vazia recebida")
            return jsonify({'error': 'A mensagem está vazia.'}), 400
        
        return f(*args, **kwargs)
    return wrapper

@app.route('/api/chat', methods=['POST'])
@validate_request
def chat():
    data = request.get_json()
    user_message = data['message']
    
    try:
        logger.info(f"Processando mensagem: {user_message}")
        entities = nlp_processor.extract_entities(user_message)
        center_info = nlp_processor.get_center_info(entities)
        response = generate_response(entities, center_info)
        
        logger.info(f"Resposta gerada: {response}")
        return jsonify({
            'response': response,
            'entities': entities,
            'center_info': center_info
        })
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({
            'error': 'Erro interno no processamento da mensagem',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'details': {
            'nlp_processor': 'active',
            'model': 'pt_core_news_sm'
        }
    })

def generate_response(entities: dict, centers_info: Optional[List[Dict]]) -> str:
    if not centers_info:
        return "Não encontrei centros de saúde com essas informações. Tente especificar o nome, bairro ou distrito."

    centros_por_bairro = {}
    for center in centers_info:
        bairro = center.get('NOME_BAIRRO_POPULAR_CS', 'Desconhecido')
        if bairro not in centros_por_bairro:
            centros_por_bairro[bairro] = []
        centros_por_bairro[bairro].append(center)

    busca_por_nome = entities.get('centro_saude') is not None
    busca_por_bairro = entities.get('bairro') is not None
    busca_por_distrito = entities.get('distrito') is not None

    response_lines = []

    if busca_por_nome:
        response_lines.append(f"Encontrei {len(centers_info)} centro(s) de saúde:")
        for center in centers_info:
            nome = center['NOME_CENTRO_SAUDE']
            endereco = center['ENDERECO_COMPLETO']
            telefone = center.get('TELEFONE_CENTRO_SAUDE', 'não disponível')
            response_lines.append(
                f"<br>• <b>{nome}</b>: {endereco} | Telefone: {telefone}"
            )

    elif busca_por_bairro and len(centros_por_bairro) == 1:
        bairro = list(centros_por_bairro.keys())[0]
        response_lines.append(f"Encontrei {len(centers_info)} centro(s) de saúde no bairro {bairro}:")
        for center in centers_info:
            nome = center['NOME_CENTRO_SAUDE']
            endereco = center['ENDERECO_COMPLETO']
            telefone = center.get('TELEFONE_CENTRO_SAUDE', 'não disponível')
            response_lines.append(
                f"<br>• <b>{nome}</b>: {endereco} | Telefone: {telefone}"
            )

    else:  # Busca por distrito
        distrito = centers_info[0].get('DISTRITO_SANITARIO', 'Belo Horizonte')
        response_lines.append(f"Encontrei {len(centers_info)} centro(s) de saúde no distrito {distrito}:<br>")

        for bairro, centros in centros_por_bairro.items():
            response_lines.append(f"<br><br><b>Bairro {bairro}:</b>")
            for center in centros:
                nome = center['NOME_CENTRO_SAUDE']
                endereco = center['ENDERECO_COMPLETO']
                telefone = center.get('TELEFONE_CENTRO_SAUDE', 'não disponível')
                response_lines.append(
                    f"<br>• <b>{nome}</b>: {endereco} | Telefone: {telefone}"
                )

    return "".join(response_lines)


if __name__ == '__main__':
    app.run(debug=True)