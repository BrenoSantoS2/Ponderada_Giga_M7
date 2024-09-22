import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

// Registrar as escalas do Chart.js
Chart.register(...registerables);

const CryptoDashboard = () => {
    const [ativos, setAtivos] = useState(['BTC-USD', 'ETH-USD']);
    const [ativoSelecionado, setAtivoSelecionado] = useState('BTC-USD');
    const [metricas, setMetricas] = useState(null);
    const [previsoes, setPrevisoes] = useState([]);
    const chartRef = useRef(null);

    useEffect(() => {
        // Buscar as métricas do modelo ao selecionar um ativo
        const fetchMetricas = async () => {
            const response = await axios.post(`http://localhost:5000/testar_modelo`, { ativo: ativoSelecionado });
            setMetricas(response.data.resultados);
        };
        fetchMetricas();
    }, [ativoSelecionado]);

    const handlePrever = async () => {
        const response = await axios.post(`http://localhost:5000/prever_valores`, { ativo: ativoSelecionado });
        setPrevisoes(response.data.previsoes);
    };

    return (
        <div>
            <h1>Dashboard de Criptoativos</h1>
            <select onChange={(e) => setAtivoSelecionado(e.target.value)}>
                {ativos.map(ativo => (
                    <option key={ativo} value={ativo}>{ativo}</option>
                ))}
            </select>
            {metricas && <div>Métricas: {JSON.stringify(metricas)}</div>}
            <button onClick={handlePrever}>Prever Valores para os Próximos 7 Dias</button>
            {previsoes.length > 0 && (
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
                        scales: {
                            x: {
                                type: 'category', // Define a escala x como 'category'
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
            )}
        </div>
    );
};

export default CryptoDashboard;
