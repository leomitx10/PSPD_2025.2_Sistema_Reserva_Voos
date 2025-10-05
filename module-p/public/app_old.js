const API_BASE = 'http://localhost:3000/api';

// Gerenciamento de Tabs
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Buscar Voos
document.getElementById('flight-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const params = {
        origem: document.getElementById('flight-origem').value,
        destino: document.getElementById('flight-destino').value,
        data: document.getElementById('flight-data').value,
        preco_max: parseFloat(document.getElementById('flight-preco').value) || 0,
        companhia_aerea: document.getElementById('flight-companhia').value,
        faixa_horario: document.getElementById('flight-horario').value,
        ordenacao: document.getElementById('flight-ordenacao').value
    };

    await searchFlights(params);
});

async function searchFlights(params) {
    const resultsDiv = document.getElementById('flight-results');
    const loadingDiv = document.getElementById('loading');

    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/flights/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar voos');
        }

        displayFlights(data);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayFlights(data) {
    const resultsDiv = document.getElementById('flight-results');
    const flights = data.voos || [];

    if (flights.length === 0) {
        resultsDiv.innerHTML = `
            <div class="empty-state">
                <h3>✈️ Nenhum voo encontrado</h3>
                <p>Tente ajustar os filtros de busca</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="result-header">
            <h3>Voos Encontrados</h3>
            <span class="result-count">${data.total_encontrados} resultados</span>
        </div>
    `;

    flights.forEach(flight => {
        html += `
            <div class="flight-card">
                <div class="card-header">
                    <div class="card-title">
                        ${flight.origem} → ${flight.destino}
                        <span class="badge">${flight.companhia_aerea}</span>
                    </div>
                    <div class="card-price">R$ ${flight.preco.toFixed(2)}</div>
                </div>
                <div class="card-details">
                    <div class="detail-item">📅 ${formatDate(flight.data)}</div>
                    <div class="detail-item">🕐 ${flight.horario_partida} - ${flight.horario_chegada}</div>
                    <div class="detail-item">⏱️ ${flight.duracao_minutos} min</div>
                    <div class="detail-item">✈️ ${flight.numero_voo}</div>
                    <div class="detail-item">🛫 ${flight.aeronave}</div>
                    <div class="detail-item">💺 ${flight.assentos_disponiveis} assentos</div>
                </div>
            </div>
        `;
    });

    if (data.tempo_processamento) {
        html += `<p style="text-align: center; color: #999; margin-top: 20px;">
            Processado em ${data.tempo_processamento}
        </p>`;
    }

    resultsDiv.innerHTML = html;
}

// Buscar Hotéis
document.getElementById('hotel-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const params = {
        city: document.getElementById('hotel-city').value,
        min_stars: parseInt(document.getElementById('hotel-min-stars').value) || 0,
        max_stars: parseInt(document.getElementById('hotel-max-stars').value) || 0,
        min_price: parseFloat(document.getElementById('hotel-min-price').value) || 0,
        max_price: parseFloat(document.getElementById('hotel-max-price').value) || 0,
        accommodation_type: document.getElementById('hotel-type').value,
        order_by: document.getElementById('hotel-order').value
    };

    await searchHotels(params);
});

async function searchHotels(params) {
    const resultsDiv = document.getElementById('hotel-results');
    const loadingDiv = document.getElementById('loading');

    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/hotels/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar hotéis');
        }

        displayHotels(data);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayHotels(data) {
    const resultsDiv = document.getElementById('hotel-results');
    const hotels = data.hotels || [];

    if (hotels.length === 0) {
        resultsDiv.innerHTML = `
            <div class="empty-state">
                <h3>🏨 Nenhum hotel encontrado</h3>
                <p>Tente ajustar os filtros de busca</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="result-header">
            <h3>Hotéis Encontrados</h3>
            <span class="result-count">${hotels.length} resultados</span>
        </div>
    `;

    hotels.forEach(hotel => {
        const stars = '⭐'.repeat(hotel.stars);
        const availableBadge = hotel.available
            ? '<span class="badge available">✓ Disponível</span>'
            : '<span class="badge unavailable">✗ Indisponível</span>';

        html += `
            <div class="hotel-card">
                <div class="card-header">
                    <div class="card-title">
                        ${hotel.name}
                        ${availableBadge}
                    </div>
                    <div class="card-price">R$ ${hotel.price.toFixed(2)}</div>
                </div>
                <div class="card-details">
                    <div class="detail-item">📍 ${hotel.city}</div>
                    <div class="detail-item"><span class="stars">${stars}</span></div>
                    <div class="detail-item">🏠 ${hotel.accommodation_type}</div>
                </div>
                ${hotel.amenities && hotel.amenities.length > 0 ? `
                    <div class="amenities">
                        ${hotel.amenities.map(a => `<span class="amenity">${a}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

// Buscar Pacotes
document.getElementById('package-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const params = {
        origem: document.getElementById('package-origem').value,
        destino: document.getElementById('package-destino').value,
        data: document.getElementById('package-data').value,
        max_budget: parseFloat(document.getElementById('package-budget').value) || 0
    };

    await searchPackages(params);
});

async function searchPackages(params) {
    const resultsDiv = document.getElementById('package-results');
    const loadingDiv = document.getElementById('loading');

    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/packages/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar pacotes');
        }

        displayPackages(data);
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayPackages(data) {
    const resultsDiv = document.getElementById('package-results');
    const packages = data.packages || [];

    if (packages.length === 0) {
        resultsDiv.innerHTML = `
            <div class="empty-state">
                <h3>📦 Nenhum pacote encontrado</h3>
                <p>Tente ajustar os filtros de busca</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="result-header">
            <h3>Pacotes Encontrados</h3>
            <span class="result-count">${packages.length} pacotes</span>
        </div>
    `;

    packages.forEach((pkg, index) => {
        html += `
            <div class="package-card">
                <h3>Pacote ${index + 1}</h3>

                <div class="package-section">
                    <h4>✈️ Voo</h4>
                    <div class="card-details">
                        <div class="detail-item">${pkg.flight.origem} → ${pkg.flight.destino}</div>
                        <div class="detail-item">🕐 ${pkg.flight.horario_partida} - ${pkg.flight.horario_chegada}</div>
                        <div class="detail-item">💰 R$ ${pkg.flight.preco.toFixed(2)}</div>
                        <div class="detail-item">✈️ ${pkg.flight.companhia_aerea}</div>
                    </div>
                </div>

                <div class="package-section">
                    <h4>🏨 Hotel</h4>
                    <div class="card-details">
                        <div class="detail-item">${pkg.hotel.name}</div>
                        <div class="detail-item">📍 ${pkg.hotel.city}</div>
                        <div class="detail-item">💰 R$ ${pkg.hotel.price.toFixed(2)}</div>
                        <div class="detail-item"><span class="stars">${'⭐'.repeat(pkg.hotel.stars)}</span></div>
                    </div>
                </div>

                <div class="total-price">
                    <h3>Preço Total: R$ ${pkg.total_price.toFixed(2)}</h3>
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

// Utilitários
function formatDate(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Definir data mínima como hoje
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('flight-data').setAttribute('min', today);
    document.getElementById('package-data').setAttribute('min', today);
});
