const out = document.getElementById('out');

function log(message) {
    console.log(`[${new Date().toLocaleTimeString()}] ${message}`);
}

function showError(message) {
    out.textContent = `Error: ${message}`;
    log(`ERROR: ${message}`);
}

function show(x) {
    out.textContent = JSON.stringify(x, null, 2);
    log('Data displayed in output area');
}

async function fetchData() {
    let c = document.getElementById('cat').value;
    log(`Fetching data${c ? ` for category: ${c}` : ' (all categories)'}`);
    
    // Přidáno: Loading indicator
    out.textContent = 'Loading...';
    
    try {
        let res = await fetch('/api/data' + (c ? `?category=${c}` : ''));
        
        if (!res.ok) {
            showError(`API request failed with status ${res.status}`);
            return;
        }
        
        let data = await res.json();
        log(`Successfully fetched ${data.length} items`);
        show(data);
    } catch (error) {
        showError(`Network error: ${error.message}`);
    }
}

function subscribe() {
    log('Initializing WebSocket connection...');
    
    let s = io();
    
    s.on('connect', () => {
        log('WebSocket connected');
    });
    
    s.on('disconnect', () => {
        log('WebSocket disconnected');
    });
    
    s.on('error', (error) => {
        showError(`WebSocket error: ${error}`);
    });
    
    log('Emitting subscribe event...');
    s.emit('subscribe', {});
    
    s.on('update', d => {
        log(`Received real-time update with ${d.length} items`);
        show(d);
    });
}

// Přidáno: Auto-refresh každých 30 vteřin (volitelné)
// Odkomentuj pokud chceš používat:
// setInterval(fetchData, 30000);