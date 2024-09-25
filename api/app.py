from flask import Flask, request, jsonify
from pipeline import (
    explorar_dados,
    treinar_modelo,
    testar_modelo,
    prever_valores,
    retreinar_modelo
)

from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Minha API de Criptoativos"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/', methods=['GET'])
def api_root():
    return jsonify({"message": "Minha API de Criptoativos"})

@app.route('/explorar_dados', methods=['GET'])
def api_explorar_dados():
    ativo = request.args.get('ativo', 'BTC-USD')
    explorar_dados(ativo)
    return jsonify({"message": f"Dados de {ativo} colhidos com sucesso."})

@app.route('/treinar_modelo', methods=['POST'])
def api_treinar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    treinar_modelo(ativo)
    return jsonify({"message": f"Modelo para {ativo} criado com sucesso."})

@app.route('/testar_modelo', methods=['POST'])
def api_testar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    resultados = testar_modelo(ativo)
    return jsonify({"message": f"Teste do modelo para {ativo} realizado com sucesso.", "resultados": resultados})

@app.route('/prever_valores', methods=['POST'])
def api_prever_valores():
    ativo = request.json.get('ativo', 'BTC-USD')
    previsoes = prever_valores(ativo, prevision_days=7)
    return jsonify({"message": f"Previsões para {ativo} geradas com sucesso.", "previsoes": previsoes.tolist()})

@app.route('/retreinar_modelo', methods=['POST'])
def api_retreinar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    retreinar_modelo(ativo)
    return jsonify({"message": f"Modelo para {ativo} foi retreinado com sucesso."})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

