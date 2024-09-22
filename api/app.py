from flask import Flask, request, jsonify
from pipeline import (
    explorar_dados,
    treinar_modelo,
    testar_modelo,
    prever_valores
)

from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Configurações do Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Você vai criar esse arquivo depois

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Minha API de Criptoativos"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/explorar_dados', methods=['GET'])
def api_explorar_dados():
    ativo = request.args.get('ativo', 'BTC-USD')  # Padrão BTC-USD se não fornecido
    explorar_dados(ativo)
    return jsonify({"message": f"Dados de {ativo} colhidos com sucesso."})

@app.route('/treinar_modelo', methods=['POST'])
def api_treinar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')  # Padrão BTC-USD se não fornecido
    treinar_modelo(ativo)
    return jsonify({"message": f"Modelo para {ativo} criado com sucesso."})

@app.route('/testar_modelo', methods=['POST'])
def api_testar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')  # Padrão BTC-USD se não fornecido
    resultados = testar_modelo(ativo)
    return jsonify({"message": f"Teste do modelo para {ativo} realizado com sucesso.", "resultados": resultados})

@app.route('/prever_valores', methods=['POST'])
def api_prever_valores():
    ativo = request.json.get('ativo', 'BTC-USD')  # Padrão BTC-USD se não fornecido
    previsoes = prever_valores(ativo, prevision_days=7)
    return jsonify({"message": f"Previsões para {ativo} geradas com sucesso.", "previsoes": previsoes.tolist()})

if __name__ == '__main__':
    app.run(debug=True)

