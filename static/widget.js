(function() {
    // ----------------------------------------------------
    // 1. CONFIGURATION (Script Attributes se aata hai)
    // ----------------------------------------------------
    const scriptTag = document.currentScript;
    
    const API_KEY = scriptTag.getAttribute("data-api-key"); 
    const API_URL = scriptTag.getAttribute("data-api-url");
    const THEME_COLOR = scriptTag.getAttribute("data-theme-color") || "#0084FF"; 

    if (!API_KEY || !API_URL) {
        console.error("OmniAgent Security Error: data-api-key or data-api-url is missing!");
        return;
    }

    // ----------------------------------------------------
    // 2. STYLES (Modern Glassmorphism + Responsive)
    // ----------------------------------------------------
    const style = document.createElement('style');
    style.innerHTML = `
        #omni-widget-container {
            position: fixed; bottom: 20px; right: 20px; z-index: 999999; 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        #omni-chat-btn {
            background: ${THEME_COLOR}; color: white; border: none; padding: 15px; border-radius: 50%;
            cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); width: 60px; height: 60px; font-size: 28px;
            display: flex; align-items: center; justify-content: center; transition: all 0.3s;
        }
        #omni-chat-btn:hover { transform: scale(1.1); }
        
        #omni-window {
            display: none; width: 380px; height: 550px; background: rgba(15, 23, 42, 0.95);
            border-radius: 16px; flex-direction: column; overflow: hidden;
            margin-bottom: 20px; animation: omniSlideUp 0.3s ease; 
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }
        
        @keyframes omniSlideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        #omni-header {
            background: ${THEME_COLOR}; padding: 15px; color: white; display: flex; justify-content: space-between; align-items: center;
        }
        .omni-title { font-weight: bold; font-size: 16px; display: flex; align-items: center; gap: 8px; }
        .omni-close { cursor: pointer; font-size: 24px; line-height: 16px; }

        #omni-visual-area { flex: 1; padding: 20px; display: flex; flex-direction: column; align-items: center; overflow-y: auto; text-align: center; }
        
        #omni-upload-box { 
            border: 2px dashed rgba(255, 255, 255, 0.3); border-radius: 12px; padding: 30px; margin-bottom: 20px; 
            width: 80%; cursor: pointer; transition: 0.2s; background: rgba(255, 255, 255, 0.05);
            color: #94a3b8;
        }
        #omni-upload-box:hover { border-color: ${THEME_COLOR}; background: rgba(255, 255, 255, 0.1); }
        #omni-file-input { display: none; }

        .omni-loader { border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid ${THEME_COLOR}; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; margin: 20px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .omni-result-card { 
            display: flex; align-items: center; gap: 10px; background: rgba(255, 255, 255, 0.1); 
            border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; width: 100%; margin-bottom: 10px; text-align: left;
            transition: 0.2s; text-decoration: none; color: white;
        }
        .omni-result-card:hover { transform: translateY(-2px); background: rgba(255, 255, 255, 0.15); }
        .omni-result-img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
        .omni-result-title { font-size: 13px; font-weight: bold; color: white; }
        .omni-result-score { font-size: 12px; color: #4ade80; }
    `;
    document.head.appendChild(style);

    // ----------------------------------------------------
    // 3. HTML STRUCTURE (Sirf Visual Search)
    // ----------------------------------------------------
    const container = document.createElement('div');
    container.id = 'omni-widget-container';

    container.innerHTML = `
        <div id="omni-window">
            <div id="omni-header">
                <div class="omni-title">🔍 Visual Search</div>
                <span class="omni-close" onclick="window.toggleOmni()">×</span>
            </div>
            
            <div id="omni-visual-area">
                <div id="omni-upload-box" onclick="document.getElementById('omni-file-input').click()">
                    <div style="font-size:40px; margin-bottom:10px;">📤</div>
                    <p style="margin:0;">Click to Upload Image</p>
                    <p style="margin:0; font-size:12px; opacity:0.7;">Find similar products</p>
                </div>
                <input type="file" id="omni-file-input" accept="image/*">
                <div id="omni-visual-loader" class="omni-loader"></div>
                <div id="omni-visual-results" style="width:100%;"></div>
            </div>
        </div>
        <button id="omni-chat-btn" onclick="window.toggleOmni()">🔍</button>
    `;

    document.body.appendChild(container);

    // ----------------------------------------------------
    // 4. UI LOGIC (Toggle Window)
    // ----------------------------------------------------
    window.toggleOmni = function() {
        const win = document.getElementById('omni-window');
        const isVisible = win.style.display === 'flex';
        win.style.display = isVisible ? 'none' : 'flex';
    };

    // ----------------------------------------------------
    // 5. VISUAL SEARCH ENGINE
    // ----------------------------------------------------
    const fileInput = document.getElementById('omni-file-input');
    const visualLoader = document.getElementById('omni-visual-loader');
    const visualResults = document.getElementById('omni-visual-results');

    fileInput.onchange = async function() {
        const file = fileInput.files[0];
        if (!file) return;

        visualLoader.style.display = 'block';
        visualResults.innerHTML = '';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/api/v1/visual/search`, {
                method: 'POST',
                headers: { 
                    'x-api-key': API_KEY // 🔐 Security Header
                },
                body: formData
            });

            const data = await response.json();
            visualLoader.style.display = 'none';

            if (!response.ok) {
                visualResults.innerHTML = `<p style="color:#f87171; margin-top:20px;">Error: ${data.detail}</p>`;
                return;
            }

            if (!data.results || data.results.length === 0) {
                visualResults.innerHTML = '<p style="color:#94a3b8; margin-top:20px;">No similar products found.</p>';
                return;
            }

            // Render Results (Aapke backend response ke saath match karta hai)
            data.results.forEach(item => {
                const score = Math.round(item.score * 100);
                // Payload structure use karein
                const title = item.payload?.title || 'Product';
                const slug = item.payload?.slug || '#';
                const img = item.payload?.image_url || 'https://via.placeholder.com/60';

                const el = document.createElement('a');
                el.className = 'omni-result-card';
                el.href = `/product/${slug}`;
                el.target = '_blank';
                el.innerHTML = `
                    <img src="${img}" class="omni-result-img" onerror="this.src='https://via.placeholder.com/60'">
                    <div>
                        <div class="omni-result-title">${title}</div>
                        <div class="omni-result-score">${score}% Match</div>
                    </div>
                `;
                visualResults.appendChild(el);
            });

        } catch (e) {
            visualLoader.style.display = 'none';
            visualResults.innerHTML = '<p style="color:#f87171;">Connection Failed</p>';
        }
    };

})();