// ============================================
// static/js/main.js - Fixed Version with Proper Rendering
// ============================================

// Generate unique session ID
const sessionId = 'session-' + Date.now();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set session ID
    document.getElementById('sessionId').textContent = sessionId;
    
    // Load dashboard data
    loadDashboard();
    
    // Set up Enter key handler
    document.getElementById('queryInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analyzeQuery();
        }
    });
    
    // Refresh dashboard every 30 seconds
    setInterval(loadDashboard, 30000);
});

function setQuery(query) {
    document.getElementById('queryInput').value = query;
    // Optional: focus the textarea
    document.getElementById('queryInput').focus();
}

async function loadDashboard() {
    try {
        // Load stock data
        const stockResp = await fetch('/api/financial-data?type=stock&symbol=AAPL');
        const stockData = await stockResp.json();
        
        document.getElementById('stockPrice').textContent = '$' + (stockData.price || 0).toFixed(2);
        const changeClass = stockData.change >= 0 ? 'positive' : 'negative';
        document.getElementById('stockChange').textContent = stockData.change_percent || 'N/A';
        document.getElementById('stockChange').className = 'change ' + changeClass;
        
        // Load transaction data
        const txnResp = await fetch('/api/financial-data?type=transactions');
        const txnData = await txnResp.json();
        const highRisk = txnData.filter(t => t.risk_score > 0.7).length;
        document.getElementById('riskCount').textContent = highRisk;
        
        // Load compliance data
        const compResp = await fetch('/api/financial-data?type=compliance');
        const compData = await compResp.json();
        document.getElementById('complianceScore').textContent = 
            (compData.sox_compliance?.compliance_score || 0).toFixed(1) + '%';
        
        // Active alerts (from AML monitoring)
        document.getElementById('alertCount').textContent = 
            compData.aml_monitoring?.suspicious_activities || 0;
            
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function formatResponse(responseText) {
    /**
     * Format the response text by:
     * 1. Unescaping newlines and unicode characters
     * 2. Converting markdown to HTML
     * 3. Preserving whitespace and formatting
     */
    
    // First, try to parse if it's a JSON string
    let text = responseText;
    try {
        // Check if it's wrapped in quotes (JSON string)
        if (text.startsWith('"') && text.endsWith('"')) {
            text = JSON.parse(text);
        }
    } catch (e) {
        // Not JSON, continue with original text
    }
    
    // Replace escaped newlines with actual line breaks
    text = text.replace(/\\n/g, '\n');
    
    // Unescape Unicode characters (emojis)
    text = text.replace(/\\u[\dA-Fa-f]{4}/g, function(match) {
        return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
    });
    
    // Convert markdown headers to HTML
    text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Convert markdown bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert markdown lists
    text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // Convert newlines to <br> tags (but not inside HTML tags)
    text = text.replace(/\n/g, '<br>');
    
    // Clean up any double breaks
    text = text.replace(/<br><br>/g, '<br>');
    
    return text;
}

async function analyzeQuery() {
    const query = document.getElementById('queryInput').value.trim();
    
    if (!query) {
        alert('Please enter a query');
        return;
    }
    
    // Show loading
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('responseSection').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Hide loading
        document.getElementById('loadingSection').style.display = 'none';
        
        if (data.success) {
            // Show results with proper formatting
            const formattedResponse = formatResponse(data.response);
            document.getElementById('responseContent').innerHTML = formattedResponse;
            document.getElementById('agentsBadge').textContent = 
                data.agents_invoked.length + ' agents invoked';
            document.getElementById('responseSection').style.display = 'block';
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
        }
        
    } catch (error) {
        document.getElementById('loadingSection').style.display = 'none';
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function clearResults() {
    document.getElementById('queryInput').value = '';
    document.getElementById('responseSection').style.display = 'none';
}
