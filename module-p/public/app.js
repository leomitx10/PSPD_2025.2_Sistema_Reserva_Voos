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

// ============ VOOS ============

// Controle de tipo de viagem
document.querySelectorAll('input[name="trip_type"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const returnDateGroup = document.getElementById('return-date-group');
        if (e.target.value === 'roundtrip') {
            //returnDateGroup.style.display = 'block';
            document.getElementById('flight-return-date').required = true;
        } else {
            returnDateGroup.style.display = 'none';
            document.getElementById('flight-return-date').required = false;
        }
    });
});

// Controle de datas flexíveis (Voos)
document.getElementById('flexible-dates-toggle').addEventListener('change', (e) => {
    const departureDate = document.getElementById('flight-departure-date');
    const returnDate = document.getElementById('flight-return-date');

    if (e.target.checked) {
        departureDate.disabled = true;
        returnDate.disabled = true;
        departureDate.required = false;
        returnDate.required = false;
    } else {
        departureDate.disabled = false;
        returnDate.disabled = false;
        departureDate.required = true;
        const tripType = document.querySelector('input[name="trip_type"]:checked').value;
        returnDate.required = (tripType === 'roundtrip');
    }
});

// Buscar Voos
document.getElementById('flight-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const flexibleDates = document.getElementById('flexible-dates-toggle').checked;

    const params = {
        origem: document.getElementById('flight-origin').value,
        destino: document.getElementById('flight-destination').value,
        data: flexibleDates ? '' : document.getElementById('flight-departure-date').value,
        data_volta: flexibleDates ? '' : document.getElementById('flight-return-date').value,
        preco_max: parseFloat(document.getElementById('flight-budget').value) || 0,
        companhia_aerea: document.getElementById('flight-companhia').value,
        faixa_horario: document.getElementById('flight-horario').value,
        ordenacao: document.getElementById('flight-ordenacao').value,
        classe: document.getElementById('flight-class').value,
        passageiros: parseInt(document.getElementById('flight-passengers').value) || 1,
        tipo_viagem: document.querySelector('input[name="trip_type"]:checked').value,
        datas_flexiveis: flexibleDates
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
                <p>Tente ajustar os filtros de busca ou ative "datas flexíveis"</p>
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
        const classeBadge = flight.classe_economica ?
            `<span class="badge class-badge">${flight.classe_economica}</span>` : '';

        html += `
            <div class="flight-card">
                <div class="card-header">
                    <div class="card-title">
                        ${flight.origem} → ${flight.destino}
                        <span class="badge">${flight.companhia_aerea}</span>
                        ${classeBadge}
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

// ============ HOTÉIS ============

// Controle de datas flexíveis (Hotéis)
document.getElementById('flexible-stay-toggle').addEventListener('change', (e) => {
    const checkin = document.getElementById('hotel-checkin');
    const checkout = document.getElementById('hotel-checkout');

    if (e.target.checked) {
        checkin.disabled = true;
        checkout.disabled = true;
        checkin.required = false;
        checkout.required = false;
    } else {
        checkin.disabled = false;
        checkout.disabled = false;
        checkin.required = true;
        checkout.required = true;
    }
});

// Buscar Hotéis
document.getElementById('hotel-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const flexibleStay = document.getElementById('flexible-stay-toggle').checked;

    const params = {
        city: document.getElementById('hotel-destination').value,
        checkin: flexibleStay ? '' : document.getElementById('hotel-checkin').value,
        checkout: flexibleStay ? '' : document.getElementById('hotel-checkout').value,
        min_stars: parseInt(document.getElementById('hotel-min-rating').value) || 0,
        max_price: parseFloat(document.getElementById('hotel-budget').value) || 0,
        accommodation_type: document.getElementById('hotel-type').value,
        order_by: document.getElementById('hotel-order').value,
        rooms: parseInt(document.getElementById('hotel-rooms').value) || 1,
        guests: parseInt(document.getElementById('hotel-guests').value) || 1,
        datas_flexiveis: flexibleStay
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
                <p>Tente ajustar os filtros de busca ou ative "datas flexíveis"</p>
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
                        <span class="badge">${hotel.accommodation_type}</span>
                    </div>
                    <div class="card-price">R$ ${hotel.price.toFixed(2)}/noite</div>
                </div>
                <div class="card-details">
                    <div class="detail-item">📍 ${hotel.city}</div>
                    <div class="detail-item"><span class="stars">${stars}</span></div>
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

// ============ PACOTES ============

// Controle de datas flexíveis (Pacotes)
document.getElementById('flexible-package-toggle').addEventListener('change', (e) => {
    const startDate = document.getElementById('package-start-date');
    const endDate = document.getElementById('package-end-date');

    if (e.target.checked) {
        startDate.disabled = true;
        endDate.disabled = true;
        startDate.required = false;
        endDate.required = false;
    } else {
        startDate.disabled = false;
        endDate.disabled = false;
        startDate.required = true;
        endDate.required = true;
    }
});

// Buscar Pacotes
document.getElementById('package-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const flexiblePackage = document.getElementById('flexible-package-toggle').checked;

    const params = {
        origem: document.getElementById('package-origin').value,
        destino: document.getElementById('package-destination').value,
        data: flexiblePackage ? '' : document.getElementById('package-start-date').value,
        data_volta: flexiblePackage ? '' : document.getElementById('package-end-date').value,
        max_budget: parseFloat(document.getElementById('package-budget').value) || 0,
        rooms: parseInt(document.getElementById('package-rooms').value) || 1,
        guests: parseInt(document.getElementById('package-guests').value) || 1,
        flight_class: document.getElementById('package-flight-class').value,
        min_rating: parseInt(document.getElementById('package-min-rating').value) || 0,
        datas_flexiveis: flexiblePackage
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
                <p>Tente ajustar os filtros de busca ou ative "pacotes mais baratos"</p>
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
        const discount = pkg.total_price * 0.3; // 30% desconto
        const originalPrice = pkg.total_price / 0.7;

        html += `
            <div class="package-card">
                <div class="package-header">
                    <h3>📦 Pacote ${index + 1}</h3>
                    <span class="discount-badge">🎉 30% OFF</span>
                </div>

                <div class="package-section">
                    <h4>✈️ Voo</h4>
                    <div class="card-details">
                        <div class="detail-item">${pkg.flight.origem} → ${pkg.flight.destino}</div>
                        <div class="detail-item">🕐 ${pkg.flight.horario_partida} - ${pkg.flight.horario_chegada}</div>
                        <div class="detail-item">💰 R$ ${pkg.flight.preco.toFixed(2)}</div>
                        <div class="detail-item">✈️ ${pkg.flight.companhia_aerea}</div>
                        ${pkg.flight.classe_economica ? `<div class="detail-item">🎫 ${pkg.flight.classe_economica}</div>` : ''}
                    </div>
                </div>

                <div class="package-section">
                    <h4>🏨 Hotel</h4>
                    <div class="card-details">
                        <div class="detail-item">${pkg.hotel.name}</div>
                        <div class="detail-item">📍 ${pkg.hotel.city}</div>
                        <div class="detail-item">💰 R$ ${pkg.hotel.price.toFixed(2)}/noite</div>
                        <div class="detail-item"><span class="stars">${'⭐'.repeat(pkg.hotel.stars)}</span></div>
                    </div>
                </div>

                <div class="total-price">
                    <div class="original-price">De: R$ ${originalPrice.toFixed(2)}</div>
                    <div class="discounted-price">
                        <h3>Por apenas: R$ ${pkg.total_price.toFixed(2)}</h3>
                        <span class="savings">Economize R$ ${discount.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

// ============ UTILITÁRIOS ============

function formatDate(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}

// ============ INICIALIZAÇÃO ============

document.addEventListener('DOMContentLoaded', () => {
    // Definir data mínima como hoje
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];

    // Voos
    document.getElementById('flight-departure-date').setAttribute('min', today);
    document.getElementById('flight-return-date').setAttribute('min', tomorrow.toISOString().split('T')[0]);

    // Hotéis
    document.getElementById('hotel-checkin').setAttribute('min', today);
    document.getElementById('hotel-checkout').setAttribute('min', tomorrowStr);

    // Pacotes
    document.getElementById('package-start-date').setAttribute('min', today);
    document.getElementById('package-end-date').setAttribute('min', tomorrowStr);

    // Auto-ajustar data de volta/checkout quando ida/checkin mudar
    document.getElementById('flight-departure-date').addEventListener('change', (e) => {
        const returnDate = document.getElementById('flight-return-date');
        const departureDate = new Date(e.target.value);
        departureDate.setDate(departureDate.getDate() + 1);
        returnDate.setAttribute('min', departureDate.toISOString().split('T')[0]);
    });

    document.getElementById('hotel-checkin').addEventListener('change', (e) => {
        const checkout = document.getElementById('hotel-checkout');
        const checkin = new Date(e.target.value);
        checkin.setDate(checkin.getDate() + 1);
        checkout.setAttribute('min', checkin.toISOString().split('T')[0]);
    });

    document.getElementById('package-start-date').addEventListener('change', (e) => {
        const endDate = document.getElementById('package-end-date');
        const startDate = new Date(e.target.value);
        startDate.setDate(startDate.getDate() + 1);
        endDate.setAttribute('min', startDate.toISOString().split('T')[0]);
    });
});
