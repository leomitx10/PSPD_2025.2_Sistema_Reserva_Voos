const API_BASE = '/api';

// ============ CARRINHO GLOBAL ============
let cart = [];

function addToCart(item) {
    cart.push(item);
    updateCartUI();
    showNotification(`${item.tipo.toUpperCase()} adicionado ao carrinho!`, 'success');
}

function removeFromCart(index) {
    const item = cart[index];
    cart.splice(index, 1);
    updateCartUI();
    showNotification(`${item.tipo.toUpperCase()} removido do carrinho`, 'info');
}

function updateCartUI() {
    const cartCount = document.getElementById('cart-count');
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    const emptyCart = document.getElementById('empty-cart');
    const cartContent = document.getElementById('cart-content');

    cartCount.textContent = cart.length;
    cartCount.style.display = cart.length > 0 ? 'flex' : 'none';

    if (cart.length === 0) {
        emptyCart.style.display = 'block';
        cartContent.style.display = 'none';
        return;
    }

    emptyCart.style.display = 'none';
    cartContent.style.display = 'block';

    let total = 0;
    let html = '';

    cart.forEach((item, index) => {
        total += item.preco;
        html += `
            <div class="cart-item">
                <div class="cart-item-details">
                    <div class="cart-item-type">${item.tipo.toUpperCase()}</div>
                    <div class="cart-item-title">${item.titulo}</div>
                    <div class="cart-item-subtitle">${item.subtitulo || ''}</div>
                </div>
                <div class="cart-item-right">
                    <div class="cart-item-price">R$ ${item.preco.toFixed(2)}</div>
                    <button class="btn-remove" onclick="removeFromCart(${index})" title="Remover">✕</button>
                </div>
            </div>
        `;
    });

    cartItems.innerHTML = html;
    cartTotal.textContent = `R$ ${total.toFixed(2)}`;
}

// ============ MODAIS ============
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// ============ NOTIFICAÇÕES ============
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============ GERENCIAMENTO DE TABS ============
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
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[name="trip_type"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const returnDateGroup = document.getElementById('return-date-group');
            if (e.target.value === 'roundtrip') {
                returnDateGroup.style.display = 'flex';
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
});

// Buscar Voos
document.getElementById('flight-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const dataIda = document.getElementById('flight-departure-date').value;
        const dataVolta = document.getElementById('flight-return-date').value || '';
        const tipoViagem = document.querySelector('input[name="trip_type"]:checked').value;

        // Validar que data de volta é posterior à data de ida
        if (tipoViagem === 'roundtrip' && dataVolta) {
            const ida = new Date(dataIda);
            const volta = new Date(dataVolta);

            if (volta <= ida) {
                showNotification('❌ A data de volta deve ser posterior à data de ida!', 'error');
                loading.style.display = 'none';
                return;
            }
        }

        const formData = {
            origem: document.getElementById('flight-origin').value,
            destino: document.getElementById('flight-destination').value,
            data: dataIda,
            data_volta: dataVolta,
            passageiros: parseInt(document.getElementById('flight-passengers').value),
            classe: document.getElementById('flight-class').value,
            companhia_aerea: document.getElementById('flight-companhia').value,
            faixa_horario: document.getElementById('flight-horario').value,
            preco_max: document.getElementById('flight-budget').value,
            ordenacao: document.getElementById('flight-ordenacao').value,
            tipo_viagem: tipoViagem,
            datas_flexiveis: document.getElementById('flexible-dates-toggle').checked
        };

        const response = await fetch(`${API_BASE}/flights/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        displayFlights(data, formData.data_volta);
    } catch (error) {
        showNotification('Erro ao buscar voos. Tente novamente.', 'error');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
});

function displayFlights(data, dataVolta) {
    const resultsDiv = document.getElementById('flight-results');
    const flights = data.voos || [];

    // GARANTIR que data_volta esteja em TODOS os voos
    if (dataVolta && flights.length > 0) {
        flights.forEach(flight => {
            flight.data_volta = dataVolta; // Força adicionar a todos
        });
    }

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
        const duracaoHoras = Math.floor(flight.duracao_minutos / 60);
        const duracaoMinutos = flight.duracao_minutos % 60;
        const duracaoFormatada = `${duracaoHoras}h${duracaoMinutos > 0 ? duracaoMinutos + 'min' : ''}`;

        const classeBadge = flight.classe_economica ?
            `<span class="badge class-badge">${flight.classe_economica}</span>` : '';

        const statusBadge = flight.status === 'ativo' ?
            '<span class="badge badge-success">Disponível</span>' :
            '<span class="badge badge-warning">Indisponível</span>';

        html += `
            <div class="flight-card card-enhanced">
                <div class="card-header">
                    <div class="card-title">
                        <div class="route-info">
                            <span class="city">${flight.origem}</span>
                            <span class="arrow">→</span>
                            <span class="city">${flight.destino}</span>
                        </div>
                        <div class="badges">
                            <span class="badge">${flight.companhia_aerea}</span>
                            ${classeBadge}
                            ${statusBadge}
                        </div>
                    </div>
                    <div class="card-price-section">
                        <div class="card-price">R$ ${flight.preco.toFixed(2)}</div>
                        <div class="price-subtitle">por pessoa</div>
                    </div>
                </div>
                <div class="card-details">
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon">📅</span>
                            <span class="detail-label">Data Ida</span>
                            <span class="detail-value">${formatDate(flight.data)}</span>
                        </div>
                        ${flight.data_volta ? `
                        <div class="detail-item">
                            <span class="detail-icon">📅</span>
                            <span class="detail-label">Data Volta</span>
                            <span class="detail-value">${formatDate(flight.data_volta)}</span>
                        </div>
                        ` : `
                        <div class="detail-item">
                            <span class="detail-icon">🕐</span>
                            <span class="detail-label">Horário</span>
                            <span class="detail-value">${flight.horario_partida} - ${flight.horario_chegada}</span>
                        </div>
                        `}
                    </div>
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon">⏱️</span>
                            <span class="detail-label">Duração</span>
                            <span class="detail-value">${duracaoFormatada}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">✈️</span>
                            <span class="detail-label">Voo</span>
                            <span class="detail-value">${flight.numero_voo}</span>
                        </div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon">🛫</span>
                            <span class="detail-label">Aeronave</span>
                            <span class="detail-value">${flight.aeronave}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">💺</span>
                            <span class="detail-label">Assentos</span>
                            <span class="detail-value">${flight.assentos_disponiveis} disponíveis</span>
                        </div>
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn-action btn-primary" onclick='reservarVoo(${JSON.stringify(flight)})'>
                        ✅ Reservar
                    </button>
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

function reservarVoo(flight) {
    const item = {
        tipo: 'voo',
        id: flight.id,
        titulo: `${flight.origem} → ${flight.destino}`,
        subtitulo: `${flight.companhia_aerea} - ${flight.numero_voo} - ${formatDate(flight.data)}`,
        preco: flight.preco,
        detalhes: JSON.stringify(flight)
    };

    openConfirmModal(item);
}

// ============ HOTÉIS ============
document.getElementById('hotel-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const checkin = document.getElementById('hotel-checkin').value;
        const checkout = document.getElementById('hotel-checkout').value;

        // Validar que check-out é posterior ao check-in
        if (checkin && checkout) {
            const dataCheckin = new Date(checkin);
            const dataCheckout = new Date(checkout);

            if (dataCheckout <= dataCheckin) {
                showNotification('❌ A data de check-out deve ser posterior à data de check-in!', 'error');
                loading.style.display = 'none';
                return;
            }
        }

        const formData = {
            city: document.getElementById('hotel-destination').value,
            checkin: checkin,
            checkout: checkout,
            rooms: parseInt(document.getElementById('hotel-rooms').value),
            guests: parseInt(document.getElementById('hotel-guests').value),
            accommodation_type: document.getElementById('hotel-type').value,
            min_stars: parseInt(document.getElementById('hotel-min-rating').value),
            max_price: parseFloat(document.getElementById('hotel-budget').value) || 0,
            order_by: document.getElementById('hotel-order').value,
            datas_flexiveis: document.getElementById('flexible-stay-toggle').checked
        };

        const response = await fetch(`${API_BASE}/hotels/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        displayHotels(data, formData.checkin, formData.checkout);
    } catch (error) {
        showNotification('Erro ao buscar hotéis. Tente novamente.', 'error');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
});

function displayHotels(data, checkIn, checkOut) {
    const resultsDiv = document.getElementById('hotel-results');
    const hotels = data.hotels || [];

    // GARANTIR que check-in e check-out estejam em TODOS os hotéis
    if (checkIn && checkOut && hotels.length > 0) {
        hotels.forEach(hotel => {
            hotel.checkin = checkIn;
            hotel.checkout = checkOut;
        });
    }

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
        const statusBadge = hotel.available ?
            '<span class="badge badge-success">Disponível</span>' :
            '<span class="badge badge-warning">Indisponível</span>';

        const amenitiesHtml = hotel.amenities && hotel.amenities.length > 0 ?
            hotel.amenities.slice(0, 4).map(a => `<span class="amenity-tag">${a}</span>`).join('') : '';

        html += `
            <div class="hotel-card card-enhanced">
                <div class="card-header">
                    <div class="card-title">
                        <div class="hotel-name">${hotel.name}</div>
                        <div class="hotel-location">📍 ${hotel.city}</div>
                        <div class="badges">
                            <span class="badge">${hotel.accommodation_type}</span>
                            ${statusBadge}
                        </div>
                    </div>
                    <div class="card-price-section">
                        <div class="card-price">R$ ${hotel.price.toFixed(2)}</div>
                        <div class="price-subtitle">por noite</div>
                    </div>
                </div>
                <div class="card-details">
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon">⭐</span>
                            <span class="detail-label">Avaliação</span>
                            <span class="detail-value">${stars}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">🏨</span>
                            <span class="detail-label">Tipo</span>
                            <span class="detail-value">${hotel.accommodation_type}</span>
                        </div>
                    </div>
                    ${checkIn && checkOut ? `
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-icon">📅</span>
                            <span class="detail-label">Check-in</span>
                            <span class="detail-value">${formatDate(checkIn)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-icon">📅</span>
                            <span class="detail-label">Check-out</span>
                            <span class="detail-value">${formatDate(checkOut)}</span>
                        </div>
                    </div>
                    ` : ''}
                    ${amenitiesHtml ? `
                        <div class="amenities-section">
                            <span class="detail-label">Comodidades:</span>
                            <div class="amenities-list">${amenitiesHtml}</div>
                        </div>
                    ` : ''}
                </div>
                <div class="card-actions">
                    <button class="btn-action btn-primary" onclick='reservarHotel(${JSON.stringify(hotel)})'>
                        ✅ Reservar
                    </button>
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

function reservarHotel(hotel) {
    const item = {
        tipo: 'hotel',
        id: hotel.id,
        titulo: hotel.name,
        subtitulo: `${hotel.city} - ${'⭐'.repeat(hotel.stars)}`,
        preco: hotel.price,
        detalhes: JSON.stringify(hotel)
    };

    openConfirmModal(item);
}

// ============ PACOTES ============
document.getElementById('package-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const checkinDate = document.getElementById('package-start-date').value;
        const checkoutDate = document.getElementById('package-end-date').value;

        // Validar que data final é posterior à data inicial
        if (checkinDate && checkoutDate) {
            const dataInicio = new Date(checkinDate);
            const dataFim = new Date(checkoutDate);

            if (dataFim <= dataInicio) {
                showNotification('❌ A data final do pacote deve ser posterior à data inicial!', 'error');
                loading.style.display = 'none';
                return;
            }
        }

        const checkin = new Date(checkinDate);
        const checkout = new Date(checkoutDate);
        const noites = Math.ceil((checkout - checkin) / (1000 * 60 * 60 * 24));

        const formData = {
            origem: document.getElementById('package-origin').value,
            destino: document.getElementById('package-destination').value,
            data: checkinDate,
            data_volta: checkoutDate,
            rooms: parseInt(document.getElementById('package-rooms').value),
            guests: parseInt(document.getElementById('package-guests').value),
            flight_class: document.getElementById('package-flight-class').value,
            min_rating: parseInt(document.getElementById('package-min-rating').value),
            max_budget: parseFloat(document.getElementById('package-budget').value) || 0,
            datas_flexiveis: document.getElementById('flexible-package-toggle').checked,
            noites: noites
        };

        const response = await fetch(`${API_BASE}/packages/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        displayPackages(data, noites);
    } catch (error) {
        showNotification('Erro ao buscar pacotes. Tente novamente.', 'error');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
});

function displayPackages(data, noites) {
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
            <span class="result-count">${packages.length} resultados</span>
        </div>
    `;

    packages.forEach(pkg => {
        const precoOriginal = pkg.total_price;
        const desconto = precoOriginal * 0.30;
        const precoFinal = precoOriginal - desconto;

        const duracaoHoras = Math.floor((pkg.flight.duracao_minutos || 0) / 60);
        const duracaoMinutos = (pkg.flight.duracao_minutos || 0) % 60;
        const duracaoFormatada = duracaoHoras > 0 ?
            `${duracaoHoras}h${duracaoMinutos > 0 ? duracaoMinutos + 'min' : ''}` :
            `${duracaoMinutos}min`;

        html += `
            <div class="package-card card-enhanced">
                <div class="package-header">
                    <div class="discount-badge">30% OFF</div>
                    <h3>${pkg.flight.origem} → ${pkg.flight.destino}</h3>
                    <p class="package-duration">${noites || 1} noite${noites > 1 ? 's' : ''}</p>
                </div>

                <div class="package-section">
                    <h4>✈️ Voo</h4>
                    <div class="card-details">
                        <div class="detail-row">
                            <div class="detail-item">
                                <span class="detail-label">Companhia</span>
                                <span class="detail-value">${pkg.flight.companhia_aerea} - ${pkg.flight.numero_voo}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Duração</span>
                                <span class="detail-value">${duracaoFormatada}</span>
                            </div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-item">
                                <span class="detail-label">Data Ida</span>
                                <span class="detail-value">${formatDate(pkg.flight.data)}</span>
                            </div>
                            ${pkg.flight.data_volta ? `
                            <div class="detail-item">
                                <span class="detail-label">Data Volta</span>
                                <span class="detail-value">${formatDate(pkg.flight.data_volta)}</span>
                            </div>
                            ` : `
                            <div class="detail-item">
                                <span class="detail-label">Horário</span>
                                <span class="detail-value">${pkg.flight.horario_partida} - ${pkg.flight.horario_chegada}</span>
                            </div>
                            `}
                        </div>
                    </div>
                </div>

                <div class="package-section">
                    <h4>🏨 Hotel - ${pkg.hotel.nights || noites} noite${(pkg.hotel.nights || noites) > 1 ? 's' : ''}</h4>
                    <div class="card-details">
                        <div class="detail-row">
                            <div class="detail-item">
                                <span class="detail-label">Nome</span>
                                <span class="detail-value">${pkg.hotel.name}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Avaliação</span>
                                <span class="detail-value">${'⭐'.repeat(pkg.hotel.stars)}</span>
                            </div>
                        </div>
                        ${pkg.hotel.checkin && pkg.hotel.checkout ? `
                        <div class="detail-row">
                            <div class="detail-item">
                                <span class="detail-label">Check-in</span>
                                <span class="detail-value">${formatDate(pkg.hotel.checkin)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Check-out</span>
                                <span class="detail-value">${formatDate(pkg.hotel.checkout)}</span>
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>

                <div class="package-pricing">
                    <div class="price-breakdown">
                        <span class="original-price">De R$ ${precoOriginal.toFixed(2)}</span>
                        <span class="savings">Economia de R$ ${desconto.toFixed(2)}</span>
                    </div>
                    <div class="final-price">
                        <span class="price-label">Por</span>
                        <span class="discounted-price">R$ ${precoFinal.toFixed(2)}</span>
                    </div>
                </div>

                <div class="card-actions">
                    <button class="btn-action btn-primary" onclick='reservarPacote(${JSON.stringify(pkg)}, ${noites}, ${precoFinal})'>
                        ✅ Reservar Pacote
                    </button>
                </div>
            </div>
        `;
    });

    resultsDiv.innerHTML = html;
}

function reservarPacote(pkg, noites, precoFinal) {
    const item = {
        tipo: 'pacote',
        id: `PKG-${pkg.flight.id}-${pkg.hotel.id}`,
        titulo: `${pkg.flight.origem} → ${pkg.flight.destino} (${noites} noite${noites > 1 ? 's' : ''})`,
        subtitulo: `${pkg.flight.companhia_aerea} + ${pkg.hotel.name}`,
        preco: precoFinal,
        detalhes: JSON.stringify(pkg)
    };

    openConfirmModal(item);
}

// ============ MODAL DE CONFIRMAÇÃO ============
function openConfirmModal(item) {
    document.getElementById('confirm-item-type').textContent = item.tipo.toUpperCase();
    document.getElementById('confirm-item-title').textContent = item.titulo;
    document.getElementById('confirm-item-subtitle').textContent = item.subtitulo;
    document.getElementById('confirm-item-price').textContent = `R$ ${item.preco.toFixed(2)}`;

    document.getElementById('btn-confirm-reservation').onclick = () => {
        addToCart(item);
        closeModal('confirm-modal');
    };

    openModal('confirm-modal');
}

// ============ FINALIZAR COMPRA (Client Streaming) ============
async function finalizarCompra() {
    if (cart.length === 0) {
        showNotification('Carrinho vazio!', 'warning');
        return;
    }

    const loading = document.getElementById('loading');
    loading.style.display = 'flex';

    try {
        const response = await fetch(`${API_BASE}/cart/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: cart })
        });

        const result = await response.json();

        if (result.sucesso) {
            // Build confirmation message with codes per type
            let codigosText = '';
            if (result.codigos && result.codigos.length > 0) {
                result.codigos.forEach(item => {
                    const tipoLabel = item.tipo.toUpperCase();
                    codigosText += `\n${tipoLabel}: ${item.codigo} (R$ ${item.valor.toFixed(2)})`;
                });
            }

            showNotification('✅ Compra confirmada com sucesso!', 'success');
            cart = [];
            updateCartUI();
            closeModal('cart-modal');

            // Show confirmation details with separate codes
            alert(`Compra Confirmada!\n\nCódigos de Confirmação:${codigosText}\n\nTotal: R$ ${result.valor_total.toFixed(2)}\nItens: ${result.total_itens}\n\nConfirmação enviada por email!`);
        } else {
            showNotification('Erro ao processar compra', 'error');
        }
    } catch (error) {
        showNotification('Erro ao finalizar compra. Tente novamente.', 'error');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

// ============ MONITORAR VOO (Server Streaming) ============
let monitorEventSource = null;

function openMonitorModal() {
    // Reset modal state
    document.getElementById('monitor-input-section').style.display = 'block';
    document.getElementById('monitor-tracking-section').style.display = 'none';
    document.getElementById('monitor-flight-code').value = '';
    document.getElementById('monitor-updates').innerHTML = '';
    document.getElementById('monitor-progress').style.width = '0%';
    document.getElementById('new-monitoring-btn').style.display = 'none';
    openModal('monitor-modal');
}

function startMonitoringFromInput() {
    const numeroVoo = document.getElementById('monitor-flight-code').value.trim();

    if (!numeroVoo) {
        showNotification('Por favor, informe o código do voo', 'warning');
        return;
    }

    // Hide input, show tracking section
    document.getElementById('monitor-input-section').style.display = 'none';
    document.getElementById('monitor-tracking-section').style.display = 'block';
    document.getElementById('monitor-flight-number').textContent = numeroVoo;

    startMonitoring(numeroVoo);
}

function startMonitoring(numeroVoo) {
    // Close previous connection if exists
    if (monitorEventSource) {
        monitorEventSource.close();
    }

    const updatesDiv = document.getElementById('monitor-updates');
    const progressBar = document.getElementById('monitor-progress');

    // Use EventSource for Server-Sent Events (alternative to gRPC streaming in browser)
    monitorEventSource = new EventSource(`${API_BASE}/flights/monitor/${numeroVoo}`);

    monitorEventSource.onmessage = (event) => {
        const update = JSON.parse(event.data);

        // Add update to list
        const updateElement = document.createElement('div');
        updateElement.className = 'monitor-update';
        updateElement.innerHTML = `
            <div class="update-time">${update.timestamp}</div>
            <div class="update-status">${update.status}</div>
            <div class="update-message">${update.mensagem}</div>
        `;
        updatesDiv.insertBefore(updateElement, updatesDiv.firstChild);

        // Update progress bar
        progressBar.style.width = `${update.progresso_percentual}%`;

        // Close connection when finished
        if (update.status === 'finalizado') {
            monitorEventSource.close();
            showNotification('Monitoramento concluído!', 'success');
            // Mostrar botão de novo monitoramento
            document.getElementById('new-monitoring-btn').style.display = 'block';
        }
    };

    monitorEventSource.onerror = () => {
        monitorEventSource.close();
        showNotification('Erro no monitoramento', 'error');
    };
}

// Função para resetar o monitoramento e permitir um novo
function resetMonitoring() {
    // Fechar conexão se estiver ativa
    if (monitorEventSource) {
        monitorEventSource.close();
        monitorEventSource = null;
    }
    
    // Resetar estado da modal
    document.getElementById('monitor-input-section').style.display = 'block';
    document.getElementById('monitor-tracking-section').style.display = 'none';
    document.getElementById('monitor-flight-code').value = '';
    document.getElementById('monitor-updates').innerHTML = '';
    document.getElementById('monitor-progress').style.width = '0%';
    document.getElementById('new-monitoring-btn').style.display = 'none';
    
    showNotification('Pronto para novo monitoramento!', 'info');
}

// ============ CHAT SUPORTE (Bidirectional Streaming) ============
let chatWebSocket = null;

function openChatModal() {
    openModal('chat-modal');
    if (!chatWebSocket || chatWebSocket.readyState === WebSocket.CLOSED) {
        connectChat();
    }
}

function connectChat() {
    const messagesDiv = document.getElementById('chat-messages');

    // Build WebSocket URL dynamically based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/chat`;
    
    // Use WebSocket for bidirectional communication (alternative to gRPC bidirectional streaming)
    chatWebSocket = new WebSocket(wsUrl);

    chatWebSocket.onopen = () => {
        addChatMessage('suporte', 'Olá! Como posso ajudar você hoje?');
    };

    chatWebSocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        addChatMessage(message.usuario, message.mensagem);
    };

    chatWebSocket.onerror = () => {
        addChatMessage('sistema', 'Erro de conexão. Tente novamente.');
    };
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to UI
    addChatMessage('cliente', message);

    // Send to server
    if (chatWebSocket && chatWebSocket.readyState === WebSocket.OPEN) {
        chatWebSocket.send(JSON.stringify({
            usuario: 'cliente',
            mensagem: message,
            timestamp: new Date().toISOString()
        }));
    }

    input.value = '';
}

function addChatMessage(usuario, mensagem) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${usuario === 'cliente' ? 'user-message' : 'support-message'}`;
    messageElement.innerHTML = `
        <div class="message-content">${mensagem}</div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Allow Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
});

// ============ UTILITÁRIOS ============
function formatDate(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}/${month}/${year}`;
}
