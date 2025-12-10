// API Base URL
const API_BASE = '/api';

// Dark Mode
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const savedMode = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedMode) {
        document.documentElement.setAttribute('data-theme', savedMode);
    } else if (prefersDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    
    updateDarkModeIcon();
    darkModeToggle.addEventListener('click', toggleDarkMode);
}

function toggleDarkMode() {
    const htmlElement = document.documentElement;
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('darkMode', newTheme);
    updateDarkModeIcon();
}

function updateDarkModeIcon() {
    const toggle = document.getElementById('darkModeToggle');
    const icon = toggle.querySelector('i');
    const theme = document.documentElement.getAttribute('data-theme');
    
    if (theme === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeDarkMode();
    setupEventListeners();
    loadPortfolioName();
    loadStocks();
    setDefaultDates();
});

// Event Listeners
function setupEventListeners() {
    document.getElementById('addStockBtn').addEventListener('click', addStock);
    document.getElementById('analyzeBtn').addEventListener('click', analyzePortfolio);
    document.getElementById('saveNameBtn').addEventListener('click', savePortfolioName);
}

function setDefaultDates() {
    const endDate = new Date();
    const startDate = new Date(endDate.getFullYear() - 1, endDate.getMonth(), endDate.getDate());
    
    document.getElementById('startDateInput').valueAsDate = startDate;
    document.getElementById('endDateInput').valueAsDate = endDate;
}

// Portfolio Name
async function loadPortfolioName() {
    try {
        const response = await fetch(`${API_BASE}/portfolio-name`);
        const data = await response.json();
        document.getElementById('portfolioName').value = data.name;
    } catch (error) {
        console.error('Error loading portfolio name:', error);
    }
}

async function savePortfolioName() {
    const name = document.getElementById('portfolioName').value;
    
    try {
        const response = await fetch(`${API_BASE}/portfolio-name`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        const data = await response.json();
        showMessage(`Portfolio renamed to "${data.name}"`, 'success');
    } catch (error) {
        console.error('Error saving portfolio name:', error);
        showMessage('Error saving portfolio name', 'error');
    }
}

// Load Stocks
async function loadStocks() {
    try {
        const response = await fetch(`${API_BASE}/stocks`);
        const data = await response.json();
        
        const stocksList = document.getElementById('stocksList');
        
        if (data.stocks.length === 0) {
            stocksList.innerHTML = '<p class="empty-message">No stocks added yet</p>';
        } else {
            stocksList.innerHTML = data.stocks.map(ticker => `
                <div class="stock-item">
                    <span class="stock-ticker">${ticker}</span>
                    <button class="btn btn-danger" onclick="removeStock('${ticker}')">Remove</button>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading stocks:', error);
    }
}

// Add Stock
async function addStock() {
    const ticker = document.getElementById('tickerInput').value.toUpperCase();
    const start = document.getElementById('startDateInput').value;
    const end = document.getElementById('endDateInput').value;
    
    if (!ticker || !start || !end) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/stocks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker, start, end })
        });
        
        if (!response.ok) {
            const error = await response.json();
            showMessage(error.error || 'Error adding stock', 'error');
            return;
        }
        
        const data = await response.json();
        showMessage(data.message, 'success');
        document.getElementById('tickerInput').value = '';
        loadStocks();
    } catch (error) {
        console.error('Error adding stock:', error);
        showMessage('Error adding stock', 'error');
    }
}

// Remove Stock
async function removeStock(ticker) {
    if (!confirm(`Remove ${ticker} from portfolio?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/stocks/${ticker}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        showMessage(data.message, 'success');
        loadStocks();
        document.getElementById('resultsPanel').classList.add('hidden');
    } catch (error) {
        console.error('Error removing stock:', error);
        showMessage('Error removing stock', 'error');
    }
}

// Analyze Portfolio
async function analyzePortfolio() {
    try {
        // Show loading state
        document.getElementById('analyzeBtn').disabled = true;
        document.getElementById('analyzeBtn').innerHTML = '<span class="loading"></span> Analyzing...';
        
        // Get analysis data
        const analysisResponse = await fetch(`${API_BASE}/analysis`);
        if (!analysisResponse.ok) {
            const error = await analysisResponse.json();
            showMessage(error.error || 'Error analyzing portfolio', 'error');
            resetButton();
            return;
        }
        
        const analysisData = await analysisResponse.json();
        
        // Get charts
        const chartResponse = await fetch(`${API_BASE}/chart`);
        const chartData = await chartResponse.json();
        
        const correlationResponse = await fetch(`${API_BASE}/correlation`);
        const correlationData = correlationResponse.ok ? await correlationResponse.json() : null;
        
        // Get compliance check
        const complianceResponse = await fetch(`${API_BASE}/compliance/check`);
        const complianceData = complianceResponse.ok ? await complianceResponse.json() : null;
        
        // Display results
        displayResults(analysisData, chartData, correlationData);
        
        // Display compliance
        if (complianceData) {
            displayCompliance(complianceData);
        }
        
        resetButton();
        showMessage('Portfolio analysis completed', 'success');
    } catch (error) {
        console.error('Error analyzing portfolio:', error);
        showMessage('Error analyzing portfolio', 'error');
        resetButton();
    }
}

function resetButton() {
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('analyzeBtn').innerHTML = 'Analyze Portfolio';
}

// Display Results
function displayResults(analysis, chartData, correlationData) {
    // Show results panel
    document.getElementById('resultsPanel').classList.remove('hidden');
    
    // Display metrics
    const analysisResult = analysis.analysis;
    document.getElementById('annualReturn').textContent = (analysisResult.annual_return * 100).toFixed(2) + '%';
    document.getElementById('annualVolatility').textContent = (analysisResult.annual_volatility * 100).toFixed(2) + '%';
    document.getElementById('sharpeRatio').textContent = analysisResult.sharpe_ratio.toFixed(4);
    
    // Display summary table
    const summary = analysis.summary;
    const summaryHTML = `
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Start Price</th>
                    <th>End Price</th>
                    <th>Return %</th>
                </tr>
            </thead>
            <tbody>
                ${Object.entries(summary).map(([ticker, data]) => `
                    <tr>
                        <td><strong>${ticker}</strong></td>
                        <td>$${data.start_price.toFixed(2)}</td>
                        <td>$${data.end_price.toFixed(2)}</td>
                        <td class="${data.return >= 0 ? 'positive' : 'negative'}">
                            ${data.return.toFixed(2)}%
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    document.getElementById('summaryTable').innerHTML = summaryHTML;
    
    // Display charts
    document.getElementById('performanceChart').src = chartData.chart;
    
    if (correlationData && correlationData.heatmap) {
        document.getElementById('correlationChart').src = correlationData.heatmap;
    } else {
        document.getElementById('correlationChart').alt = 'Need at least 2 stocks for correlation';
    }
    
    // Scroll to results
    document.getElementById('resultsPanel').scrollIntoView({ behavior: 'smooth' });
}

// Compliance Monitoring
function displayCompliance(complianceData) {
    // Update compliance score
    const scoreElement = document.getElementById('complianceScore');
    const scoreValueElement = scoreElement.querySelector('.score-value');
    const score = ((complianceData.compliant / complianceData.total_rules) * 100).toFixed(0);
    scoreValueElement.textContent = score + '%';
    
    // Update score styling based on overall status
    scoreElement.classList.remove('warning', 'non-compliant');
    if (complianceData.overall_status === 'non_compliant') {
        scoreElement.classList.add('non-compliant');
    } else if (complianceData.overall_status === 'warning') {
        scoreElement.classList.add('warning');
    }
    
    // Update counts
    document.getElementById('compliantRulesCount').textContent = complianceData.compliant;
    document.getElementById('warningRulesCount').textContent = complianceData.warnings;
    document.getElementById('nonCompliantRulesCount').textContent = complianceData.non_compliant;
    document.getElementById('totalRulesCount').textContent = complianceData.total_rules;
    
    // Display compliance checks
    const checksContainer = document.getElementById('complianceChecks');
    if (complianceData.checks && complianceData.checks.length > 0) {
        checksContainer.innerHTML = complianceData.checks.map(check => {
            const icon = check.status === 'compliant' ? 'fa-check-circle' : 
                        check.status === 'warning' ? 'fa-exclamation-circle' : 'fa-times-circle';
            
            const detailsHTML = check.details && Object.keys(check.details).length > 0 ? 
                `<div class="compliance-details">
                    ${Object.entries(check.details).map(([key, value]) => `
                        <div class="compliance-detail-item">
                            <span class="compliance-detail-label">${formatKey(key)}</span>
                            <span class="compliance-detail-value">${value}</span>
                        </div>
                    `).join('')}
                </div>` : '';
            
            return `
                <div class="compliance-check ${check.status}" onclick="toggleComplianceDetails(this)">
                    <div class="compliance-check-content">
                        <div class="compliance-check-title">
                            <span class="compliance-check-icon"><i class="fas ${icon}"></i></span>
                            <span>${check.name}</span>
                        </div>
                        <div class="compliance-check-message">${check.message}</div>
                        ${detailsHTML}
                    </div>
                    <div class="compliance-check-status">${check.status.replace('_', ' ')}</div>
                </div>
            `;
        }).join('');
    }
}

function toggleComplianceDetails(element) {
    element.classList.toggle('expanded');
}

function formatKey(key) {
    // Convert snake_case to readable format
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Messages
function showMessage(message, type) {
    // Get existing message or create new one
    let messageEl = document.querySelector('.message');
    if (!messageEl) {
        messageEl = document.createElement('div');
        messageEl.className = 'message';
        document.body.appendChild(messageEl);
    }
    
    // Add icon based on type
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>'
    };
    
    messageEl.innerHTML = (icons[type] || '') + message;
    messageEl.className = `message show ${type}`;
    
    setTimeout(() => {
        messageEl.classList.remove('show');
    }, 4000);
}
