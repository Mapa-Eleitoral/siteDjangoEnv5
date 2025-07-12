/**
 * Mapa Eleitoral - Main Application JavaScript
 * Handles form interactions, AJAX requests, and map generation
 */

class ElectoralMapApp {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.stateManager = new StateManager();
        this.performanceMonitor = new PerformanceMonitor();
    }

    init() {
        this.elements = {
            ano: document.getElementById('id_ano'),
            partido: document.getElementById('id_partido'),
            candidato: document.getElementById('id_candidato'),
            mapContainer: document.getElementById('map-iframe-container'),
            mapContent: document.getElementById('map-content'),
            generateBtn: document.getElementById('generate-map-btn'),
            statusMessage: document.getElementById('status-message')
        };

        // Initialize form state
        this.preloadCriticalData();
    }

    setupEventListeners() {
        if (this.elements.ano) {
            this.elements.ano.addEventListener('change', this.debounce(this.updatePartidos.bind(this), 300));
        }

        if (this.elements.partido) {
            this.elements.partido.addEventListener('change', this.debounce(this.updateCandidatos.bind(this), 300));
        }

        if (this.elements.generateBtn) {
            this.elements.generateBtn.addEventListener('click', this.generateMap.bind(this));
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async preloadCriticalData() {
        try {
            const anoAtual = this.elements.ano?.value;
            if (anoAtual && anoAtual !== '' && !isNaN(anoAtual)) {
                await this.stateManager.getData(
                    `/get_partidos_ajax/?ano=${encodeURIComponent(anoAtual)}`,
                    `partidos_${anoAtual}`
                );
            }
        } catch (error) {
            console.warn('Preload failed:', error);
        }
    }

    async updatePartidos() {
        const startTime = performance.now();
        const ano = this.elements.ano?.value;

        if (!ano || ano === '' || isNaN(ano) || ano.length !== 4) {
            console.warn('Ano inválido para updatePartidos:', ano);
            return;
        }

        try {
            this.setSelectLoading(this.elements.partido, true);
            this.clearSelect(this.elements.candidato);

            const cacheKey = `partidos_${ano}`;
            const data = await this.stateManager.getData(
                `/get_partidos_ajax/?ano=${encodeURIComponent(ano)}`,
                cacheKey
            );

            if (data?.partidos) {
                this.populateSelect(this.elements.partido, data.partidos);
                
                // Auto-select PSD if available
                if (data.partidos.includes('PSD')) {
                    this.elements.partido.value = 'PSD';
                    await this.updateCandidatos();
                }
            }

            this.performanceMonitor.recordOperation('updatePartidos', performance.now() - startTime);
        } catch (error) {
            this.showError('Erro ao carregar partidos: ' + error.message);
        } finally {
            this.setSelectLoading(this.elements.partido, false);
        }
    }

    async updateCandidatos() {
        const startTime = performance.now();
        const partido = this.elements.partido?.value;
        const ano = this.elements.ano?.value;

        if (!partido || !ano) return;

        try {
            this.setSelectLoading(this.elements.candidato, true);

            const cacheKey = `candidatos_${partido}_${ano}`;
            const data = await this.stateManager.getData(
                `/get_candidatos_ajax/?partido=${encodeURIComponent(partido)}&ano=${encodeURIComponent(ano)}`,
                cacheKey
            );

            if (data?.candidatos) {
                this.populateSelect(this.elements.candidato, data.candidatos);
                
                // Auto-select EDUARDO PAES if available
                if (data.candidatos.includes('EDUARDO PAES')) {
                    this.elements.candidato.value = 'EDUARDO PAES';
                }
            }

            this.performanceMonitor.recordOperation('updateCandidatos', performance.now() - startTime);
        } catch (error) {
            this.showError('Erro ao carregar candidatos: ' + error.message);
        } finally {
            this.setSelectLoading(this.elements.candidato, false);
        }
    }

    async generateMap() {
        const candidato = this.elements.candidato?.value;
        const partido = this.elements.partido?.value;
        const ano = this.elements.ano?.value;

        if (!candidato || !partido || !ano) {
            this.showError('Selecione ano, partido e candidato');
            return;
        }

        const startTime = performance.now();

        try {
            this.setButtonLoading(this.elements.generateBtn, true);
            this.showInfo('Gerando mapa... Isso pode levar alguns segundos.');

            const response = await fetch(`/generate-map/?candidato=${encodeURIComponent(candidato)}&partido=${encodeURIComponent(partido)}&ano=${encodeURIComponent(ano)}`);
            const data = await response.json();

            if (data.success) {
                this.displayMap(data.html, data.candidato_info);
                this.showSuccess(`Mapa gerado com sucesso para ${data.candidato_info.nome}`);
                
                // Track with Google Analytics
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'map_generated', {
                        'event_category': 'maps',
                        'event_label': `${candidato}_${partido}_${ano}`,
                        'value': 1
                    });
                }
            } else {
                this.showError(data.error || 'Erro ao gerar mapa');
            }

            this.performanceMonitor.recordOperation('generateMap', performance.now() - startTime);
        } catch (error) {
            this.showError('Erro de rede: ' + error.message);
        } finally {
            this.setButtonLoading(this.elements.generateBtn, false);
        }
    }

    displayMap(htmlContent, candidatoInfo) {
        if (!this.elements.mapContent) return;

        const iframe = document.createElement('iframe');
        iframe.style.width = '100%';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '8px';
        iframe.setAttribute('title', `Mapa de ${candidatoInfo.nome}`);
        
        // Responsive height based on screen size
        const isMobile = window.innerWidth <= 768;
        const isSmallMobile = window.innerWidth <= 480;
        
        if (isSmallMobile) {
            iframe.style.height = '300px';
        } else if (isMobile) {
            iframe.style.height = '350px';
        } else {
            iframe.style.height = '600px';
        }

        this.elements.mapContent.innerHTML = '';
        this.elements.mapContent.appendChild(iframe);

        iframe.onload = () => {
            iframe.contentDocument.open();
            iframe.contentDocument.write(htmlContent);
            iframe.contentDocument.close();
        };
    }

    // Utility Methods
    setSelectLoading(select, loading) {
        if (!select) return;
        
        if (loading) {
            select.disabled = true;
            select.classList.add('loading');
        } else {
            select.disabled = false;
            select.classList.remove('loading');
        }
    }

    setButtonLoading(button, loading) {
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            button.classList.add('loading');
            button.textContent = 'Gerando...';
        } else {
            button.disabled = false;
            button.classList.remove('loading');
            button.textContent = 'Gerar Mapa';
        }
    }

    clearSelect(select) {
        if (!select) return;
        select.innerHTML = '<option value="">Selecione...</option>';
    }

    populateSelect(select, options) {
        if (!select) return;
        
        select.innerHTML = '<option value="">Selecione...</option>';
        options.forEach(option => {
            const optElement = document.createElement('option');
            optElement.value = option;
            optElement.textContent = option;
            select.appendChild(optElement);
        });
    }

    showMessage(message, type) {
        if (!this.elements.statusMessage) return;
        
        this.elements.statusMessage.className = `status-message status-${type}`;
        this.elements.statusMessage.textContent = message;
        this.elements.statusMessage.style.display = 'block';
        
        setTimeout(() => {
            this.elements.statusMessage.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) { this.showMessage(message, 'success'); }
    showError(message) { this.showMessage(message, 'error'); }
    showInfo(message) { this.showMessage(message, 'info'); }
}

// State Management
class StateManager {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
    }

    async getData(url, cacheKey) {
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.cache.set(cacheKey, {
            data,
            timestamp: Date.now()
        });

        return data;
    }

    clearCache() {
        this.cache.clear();
    }
}

// Performance Monitoring
class PerformanceMonitor {
    constructor() {
        this.operations = new Map();
    }

    recordOperation(name, duration) {
        if (!this.operations.has(name)) {
            this.operations.set(name, []);
        }
        
        this.operations.get(name).push(duration);
        
        if (duration > 1000) {
            console.warn(`Slow operation: ${name} took ${duration.toFixed(2)}ms`);
        }
    }

    getStats() {
        const stats = {};
        for (const [name, durations] of this.operations) {
            const avg = durations.reduce((a, b) => a + b, 0) / durations.length;
            const max = Math.max(...durations);
            stats[name] = { avg: avg.toFixed(2), max: max.toFixed(2), count: durations.length };
        }
        return stats;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ElectoralMapApp();
    
    // Mobile-specific optimizations
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Improve touch interactions
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            select.style.fontSize = '16px'; // Prevent zoom on iOS
        });
        
        // Add touch-friendly button sizing
        const buttons = document.querySelectorAll('button, .btn');
        buttons.forEach(button => {
            if (button.style.minHeight === '') {
                button.style.minHeight = '44px';
            }
        });
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            const mapIframes = document.querySelectorAll('iframe');
            mapIframes.forEach(iframe => {
                const isMobile = window.innerWidth <= 768;
                const isSmallMobile = window.innerWidth <= 480;
                
                if (isSmallMobile) {
                    iframe.style.height = '300px';
                } else if (isMobile) {
                    iframe.style.height = '350px';
                } else {
                    iframe.style.height = '600px';
                }
            });
        }, 500); // Delay to ensure viewport has updated
    });
});

// Expose for debugging
window.ElectoralMapApp = ElectoralMapApp;