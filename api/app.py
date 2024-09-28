from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pipeline import (
    explorar_dados,
    treinar_modelo,
    testar_modelo,
    prever_valores,
    retreinar_modelo
)
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import numpy as np  # Certifique-se de importar o NumPy

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cripto_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definir tabela de logs de interação
class UserLog(db.Model):
    __tablename__ = 'user_logs'
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(50))
    ativo = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Cria a tabela no banco de dados
with app.app_context():
    db.create_all()

# Swagger e outras rotas
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Minha API de Criptoativos"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/', methods=['GET'])
def api_root():
    log_interaction('root', None)
    return jsonify({"message": "Minha API de Criptoativos"})

@app.route('/explorar_dados', methods=['GET'])
def api_explorar_dados():
    ativo = request.args.get('ativo', 'BTC-USD')
    explorar_dados(ativo)
    log_interaction('explorar_dados', ativo)
    return jsonify({"message": f"Dados de {ativo} colhidos com sucesso."})

@app.route('/treinar_modelo', methods=['POST'])
def api_treinar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    treinar_modelo(ativo)
    log_interaction('treinar_modelo', ativo)
    return jsonify({"message": f"Modelo para {ativo} criado com sucesso."})

@app.route('/testar_modelo', methods=['POST'])
def api_testar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    resultados = testar_modelo(ativo)
    log_interaction('testar_modelo', ativo)
    return jsonify({"message": f"Teste do modelo para {ativo} realizado com sucesso.", "resultados": resultados})

@app.route('/prever_valores', methods=['POST'])
def api_prever_valores():
    ativo = request.json.get('ativo', 'BTC-USD')
    previsoes, tendencia = prever_valores(ativo, prevision_days=7)
    
    # Corrigindo a serialização do array para JSON
    previsoes_list = previsoes.tolist() if isinstance(previsoes, np.ndarray) else previsoes

    log_interaction('prever_valores', ativo)
    return jsonify({
        "message": f"Previsões para {ativo} geradas com sucesso.",
        "previsoes": previsoes_list,
        "tendencia": tendencia
    })

@app.route('/retreinar_modelo', methods=['POST'])
def api_retreinar_modelo():
    ativo = request.json.get('ativo', 'BTC-USD')
    retreinar_modelo(ativo)
    log_interaction('retreinar_modelo', ativo)
    return jsonify({"message": f"Modelo para {ativo} foi retreinado com sucesso."})

@app.route('/logs', methods=['GET'])
def api_get_logs():
    logs = UserLog.query.all()
    logs_list = [{"id": log.id, "route": log.route, "ativo": log.ativo, "timestamp": log.timestamp} for log in logs]
    return jsonify(logs_list)

@app.route('/avaliar_compra', methods=['POST'])
def api_avaliar_compra():
    ativo = request.json.get('ativo', 'BTC-USD')
    previsoes, tendencia = prever_valores(ativo, prevision_days=7)
    
    recomendacao = "compra" if tendencia == "alta" else "venda"

    # Log da interação
    log_interaction('avaliar_compra', ativo)

    # Convertendo previsões em lista para JSON
    previsoes_list = previsoes.tolist() if isinstance(previsoes, np.ndarray) else previsoes

    return jsonify({
        "message": f"Recomendação para {ativo}: {recomendacao}.",
        "previsoes": previsoes_list,
        "tendencia": tendencia
    })

# Função para registrar logs de interação
def log_interaction(route, ativo):
    log = UserLog(route=route, ativo=ativo)
    db.session.add(log)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
