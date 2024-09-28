import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import './CryptoDashboard.css'; // Importando o CSS

// Registrar as escalas do Chart.js
Chart.register(...registerables);

const CryptoDashboard = () => {
    const ativos = ['BTC-USD', 'ETH-USD'];
    const [ativoSelecionado, setAtivoSelecionado] = useState('BTC-USD');
    const [metricas, setMetricas] = useState(null);
    const [previsoes, setPrevisoes] = useState([]);
    const [modeloExistente, setModeloExistente] = useState(false); // Novo estado
    const [loading, setLoading] = useState(false); // Estado de carregamento
    /* const [recomendacao, setRecomendacao] = useState(''); */

    const chartRef = useRef(null);

    useEffect(() => {
        const fetchMetricas = async () => {
            try {
                const response = await axios.post(`http://localhost:5000/testar_modelo`, { ativo: ativoSelecionado });
                setMetricas(response.data.resultados);
                setModeloExistente(true); // Se o modelo existe
            } catch (error) {
                setModeloExistente(false); // Se não existe
                setMetricas(null);
            }
        };
        fetchMetricas();
    }, [ativoSelecionado]);

    const handlePrever = async () => {
        const response = await axios.post(`http://localhost:5000/prever_valores`, { ativo: ativoSelecionado });
        setPrevisoes(response.data.previsoes);
    };

    const handleTreinar = async () => {
        console.log('Treinando o modelo...');
        setLoading(true); // Inicia o carregamento
        console.log('Ativo selecionado:', ativoSelecionado);
        const response = await axios.post(`http://localhost:5000/retreinar_modelo`, { ativo: ativoSelecionado });
        console.log('Resultado do back...');
        setPrevisoes(response.data.previsoes);
        setModeloExistente(true); // Após treinar, modelo existe
        setLoading(false); // Finaliza o carregamento
    };

    const handleRetreinar = async () => {
        setLoading(true); // Inicia o carregamento
        await axios.post(`http://localhost:5000/retreinar_modelo`, { ativo: ativoSelecionado });
        alert('Modelo retreinado com sucesso!');
        await fetchMetricas(); // Atualiza as métricas após retreinar
        setLoading(false); // Finaliza o carregamento
    };

    // Função para buscar métricas (movida para fora do useEffect para uso em handleRetreinar)
    const fetchMetricas = async () => {
        try {
            const response = await axios.post(`http://localhost:5000/testar_modelo`, { ativo: ativoSelecionado });
            setMetricas(response.data.resultados);
            setModeloExistente(true); // Se o modelo existe
        } catch (error) {
            setModeloExistente(false); // Se não existe
            setMetricas(null);
        }
    };

    /* const recomendation = async () => {
        try {
            const response = await axios.post(`http://localhost:5000/avaliar_compra`, { ativo: ativoSelecionado });
            setRecomendacao(response.data.message); // Armazenar a recomendação no estado
        } catch (error) {
            console.error("Erro ao pegar recomendação:", error);
        }
    }; */
    

    return (
        <div className="dashboard-container">
            <h1>Dashboard de Criptoativos</h1>
            <div className="controls">
                <label htmlFor="ativo-select">Selecione um ativo:</label>
                <select
                    id="ativo-select"
                    onChange={(e) => setAtivoSelecionado(e.target.value)}
                >
                    
                    {ativos.map(ativo => (
                        <option key={ativo} value={ativo}>{ativo}</option>
                    ))}
                </select>
            </div>

            {metricas && (
                <div className="metricas">
                    <h2>Métricas do Modelo</h2>
                    <ul>
                        <li><strong>Erro Médio Absoluto (MAE):</strong> {metricas[0]}</li>
                        <li><strong>Erro Quadrático Médio (MSE):</strong> {metricas[1]}</li>
                        <li><strong>Raiz do Erro Quadrático Médio (RMSE):</strong> {metricas[2]}</li>
                    </ul>
                </div>
            )}

            <div className="buttons">
                {!modeloExistente ? (
                    <button onClick={handleTreinar} disabled={loading}>
                        {loading ? 'Treinando...' : 'Treinar o modelo'}
                    </button>
                ) : (
                    <>
                        <button onClick={handlePrever}>Prever Valores para os Próximos 7 Dias</button>
                        <button onClick={handleRetreinar}>Retreinar Modelo com Dados Recentes</button>
                    </>
                )}
            </div>

            {loading && <p>Carregando... Por favor, aguarde.</p>} {/* Mensagem de carregamento */}

            {previsoes.length > 0 && (
                
                <div className="chart-container">
                    <Line
                        ref={chartRef}
                        data={{
                            labels: [...Array(previsoes.length).keys()].map(i => `Dia ${i + 1}`),
                            datasets: [{
                                label: 'Previsões',
                                data: previsoes,
                                borderColor: 'rgba(75, 192, 192, 1)',
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            }]
                        }}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false, // Manter gráfico responsivo
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Dias',
                                    },
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Valor',
                                    },
                                },
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top',
                                },
                            },
                        }}
                    />
                </div>
            )}
        </div>
    );
};

export default CryptoDashboard;
