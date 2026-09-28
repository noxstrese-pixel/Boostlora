/**
 * Nox Control System Layer v11.0 - absolute Lifecycle Fix
 * Save this file exactly as "boost.js" in the same folder as index.html
 */
(function() {
    console.log("Nox Control Core: Instantiating dynamic asset procurement framework...");

    const STORAGE_KEY = "NOX_CENTRAL_PERSISTENCE_V11";
    let STATE = null;
    let txTimer = null;

    function loadPersistedState() {
        const fallbackDefault = {
            isLoggedIn: false,
            user: { username: "", balance: 42.50 },
            activeTab: "checker",
            depositStatus: "idle",
            tokenProvider: "standard", // 'standard', 'own', 'salta7'
            storefront: [
                { id: "p1", title: "1-Month Boost Slot", basePrice: 0.15, type: "boost", description: "Allocate automated tokens to elevate targeted servers." },
                { id: "p2", title: "Premium High-Age Profile", basePrice: 0.85, type: "account", description: "Aged profiles populated with realistic media records." },
                { id: "p3", title: "Profile Management Tool", basePrice: 0.05, type: "utility", description: "Metadata restructuring script for bulk user management." }
            ]
        };

        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return fallbackDefault;
            const parsed = JSON.parse(raw);
            parsed.storefront = fallbackDefault.storefront;
            parsed.depositStatus = "idle"; 
            if (!parsed.tokenProvider) parsed.tokenProvider = "standard";
            return parsed;
        } catch (e) {
            return fallbackDefault;
        }
    }

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(STATE));
    }

    function calculateItemPrice(basePrice) {
        if (STATE.tokenProvider === "own") {
            return 0.02; // Only pay for the captcha handling fee
        }
        if (STATE.tokenProvider === "salta7") {
            return 0.18; // Fixed flat price marker per token
        }
        return basePrice;
    }

    function renderLayoutRouter() {
        if (!document.body) {
            console.error("Critical Failure: Browser body node still unavailable.");
            return;
        }
        
        document.body.innerHTML = "";

        if (!STATE.isLoggedIn) {
            document.body.innerHTML = `
                <div class="n-auth-screen" style="display: flex; align-items: center; justify-content: center; width: 100%; min-height: 100vh; background: var(--bg-main, #090D16);">
                    <div class="n-auth-card" style="background: var(--bg-card, #151D30); border: 1px solid var(--border-color, #1F293D); border-radius: 16px; padding: 40px; max-width: 400px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                        <h3 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 800; text-align: center; color: white;">System Portal Access</h3>
                        <p style="margin: 0 0 24px 0; font-size: 13px; color: var(--text-muted, #9CA3AF); text-align: center;">Enter system profile parameters to connect securely.</p>
                        
                        <div style="margin-bottom: 16px;">
                            <label style="font-size: 12px; font-weight:600; color: var(--text-muted, #9CA3AF); display:block; margin-bottom:6px;">Account Username</label>
                            <input type="text" class="n-input" id="auth-username-field" placeholder="Username..." style="width:100%; background:var(--bg-main, #090D16); color:white; border:1px solid var(--border-color, #1F293D); padding:12px; border-radius:8px; outline:none;" />
                        </div>
                        
                        <div style="margin-bottom: 24px;">
                            <label style="font-size: 12px; font-weight:600; color: var(--text-muted, #9CA3AF); display:block; margin-bottom:6px;">Security Password</label>
                            <input type="password" class="n-input" id="auth-password-field" placeholder="••••••••" style="width:100%; background:var(--bg-main, #090D16); color:white; border:1px solid var(--border-color, #1F293D); padding:12px; border-radius:8px; outline:none;" />
                        </div>
                        
                        <button class="action-btn" id="auth-submit-btn">Authenticate Session</button>
                    </div>
                </div>
            `;

            document.getElementById('auth-submit-btn').addEventListener('click', () => {
                const userVal = document.getElementById('auth-username-field').value.trim();
                const passVal = document.getElementById('auth-password-field').value.trim();
                
                if (!userVal || !passVal) {
                    alert("Both username and password fields must be filled out.");
                    return;
                }
                STATE.isLoggedIn = true;
                STATE.user.username = userVal;
                saveState();
                renderLayoutRouter();
            });
            return;
        }

        document.body.innerHTML = `
            <aside class="sidebar">
                <div class="sidebar-brand">Boostlora</div>
                <button class="nav-btn ${STATE.activeTab === 'checker' ? 'active' : ''}" id="nav-tab-checker" type="button">Account Checker</button>
                <button class="nav-btn ${STATE.activeTab === 'booster' ? 'active' : ''}" id="nav-tab-booster" type="button">Server Booster <span class="badge-dev">WIP</span></button>
                <button class="nav-btn ${STATE.activeTab === 'joiner' ? 'active' : ''}" id="nav-tab-joiner" type="button">Server Joiner <span class="badge-dev">WIP</span></button>
                
                <div class="sidebar-wallet">
                    <div class="wallet-title">User Account: <span style="color:#fff;">${STATE.user.username}</span></div>
                    <div class="wallet-title" style="margin-top: 4px;">Available Funds</div>
                    <div class="wallet-amount" id="dom-wallet-bal">$${STATE.user.balance.toFixed(2)}</div>
                    <button class="wallet-btn" id="dom-open-deposit-btn">Deposit Crypto</button>
                    <button class="wallet-btn-logout" id="dom-logout-btn">Log Out</button>
                </div>
            </aside>

            <main class="content-area">
                <div class="dashboard-container" id="dom-panel-viewport"></div>
            </main>

            <div class="n-modal-overlay" id="dom-deposit-modal">
                <div class="n-modal-box">
                    <button class="n-modal-close" id="dom-close-modal-btn">×</button>
                    <h3 style="margin:0 0 8px 0; font-size:18px; font-weight:800;">Crypto Deposit Gateway</h3>
                    <p style="font-size:13px; color:var(--text-muted); margin:0;">Send BTC to your dedicated address below to credit your balance instantly via the blockchain mempool.</p>
                    <div class="wallet-title" style="text-align:left; margin-top:20px;">Your BTC Deposit Destination</div>
                    <div class="n-address-container">bc1qnx77asecurematrixp99fflowsystem327vpx08cl83a</div>
                    <div style="margin-top:24px;">
                        <div class="n-badge-status" id="dom-modal-status-badge">
                            <div class="spinner" id="dom-modal-spinner"></div>
                            <span id="dom-modal-status-text">Awaiting network transaction broadcast...</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('nav-tab-checker').addEventListener('click', () => switchTab('checker'));
        document.getElementById('nav-tab-booster').addEventListener('click', () => switchTab('booster'));
        document.getElementById('nav-tab-joiner').addEventListener('click', () => switchTab('joiner'));
        
        document.getElementById('dom-logout-btn').addEventListener('click', () => {
            STATE.isLoggedIn = false;
            saveState();
            renderLayoutRouter();
        });

        drawViewportPanel();
        configureDepositModal();
    }

    function switchTab(tabId) {
        STATE.activeTab = tabId;
        saveState();
        renderLayoutRouter();
    }

    function drawViewportPanel() {
        const view = document.getElementById('dom-panel-viewport');
        if (!view) return;
        view.innerHTML = "";

        if (STATE.activeTab === "checker") {
            view.innerHTML = `
                <div class="header-section">
                    <h2>Account Checker Subsystem Matrix</h2>
                    <p class="subtitle">Input your raw configuration metrics data array parameters directly below.</p>
                </div>
                <textarea placeholder="Paste account lists here (one entry per line matrix combo)..."></textarea>
                <button class="action-btn">Launch System Verification</button>
                
                <div class="results-section">
                    <div class="status-title">Ecosystem Performance Logging</div>
                    <div class="stats-grid">
                        <div class="grid-item valid"><div class="stat-val">0</div><div class="stat-label">Verified Valid</div></div>
                        <div class="grid-item warning"><div class="stat-val">0</div><div class="stat-label">Flagged Flag</div></div>
                        <div class="grid-item invalid"><div class="stat-val">0</div><div class="stat-label">Rejected Bad</div></div>
                    </div>
                    <div class="list-container" style="padding:40px; text-align:center; color:var(--text-muted); font-size:13px;">
                        Awaiting data sequence submission queue...
                    </div>
                </div>
            `;
} else if (STATE.activeTab === "booster") {
view.innerHTML = `

Server Booster Allocation Framework
Deploy automated slot structures directly to destination tracking environments.
Infrastructure Provider:
Standard System
Own Infrastructure ($0.02 Captcha Fee)
Salta7 Nodes ($0.18 Flat Rate)
Target Invite Code Link Location
Deploy Optimization Matrix
Available Resource Inventory Procurement

`;
const radios = view.querySelectorAll('input[name="provider-select"]');
radios.forEach(radio => {
radio.addEventListener('change', (e) => {
STATE.tokenProvider = e.target.value;
saveState();
drawViewportPanel();
});
});
const storeBox = document.getElementById('dom-store-box');
STATE.storefront.forEach(item => {
const computedPrice = calculateItemPrice(item.basePrice);
const card = document.createElement('div');
card.className = 'store-card';
card.innerHTML = <div> <h4 class="store-title">${item.title}</h4> <p class="store-desc">${item.description}</p> </div> <div class="store-footer"> <div class="store-price">$${computedPrice.toFixed(2)}</div> <button class="store-btn">Procure Item</button> </div>;
card.querySelector('.store-btn').addEventListener('click', () => {
if (STATE.user.balance >= computedPrice) {
STATE.user.balance -= computedPrice;
saveState();
document.getElementById('dom-wallet-bal').innerText = $${STATE.user.balance.toFixed(2)};
alert(Successfully acquired item asset row: ${item.title});
} else {
alert("Insufficient available system balance credits.");
}
});
storeBox.appendChild(card);
});
document.getElementById('booster-exec-btn').addEventListener('click', () => {
const txt = document.getElementById('booster-lnk-input').value;
if (!txt) { alert("Please specify a targeted network endpoint code parameter."); return; }
alert("Processing optimization routines across internal inventories.");
});
} else {
view.innerHTML = <div class="header-section"> <h2>Server Joiner Sandbox Module</h2> <p class="subtitle">System engine sandbox architecture workspace environment tools.</p> </div> <div style="padding:60px; text-align:center; border: 1px dashed var(--border-color); border-radius:12px; color:var(--text-muted); font-size:13px;"> Sandbox tool deployment modules are processing under active construction. </div>;
}
}
function configureDepositModal() {
const modal = document.getElementById('dom-deposit-modal');
const openBtn = document.getElementById('dom-open-deposit-btn');
const closeBtn = document.getElementById('dom-close-modal-btn');
const badge = document.getElementById('dom-modal-status-badge');
const spinner = document.getElementById('dom-modal-spinner');
const txt = document.getElementById('dom-modal-status-text');
if (!modal || !openBtn) return;
openBtn.addEventListener('click', () => {
modal.style.display = 'flex';
if (STATE.depositStatus === "idle") {
STATE.depositStatus = "pending";
txt.innerText = "Monitoring ledger block matrices for payment hash broadcast...";
txTimer = setTimeout(() => {
STATE.depositStatus = "confirmed";
STATE.user.balance += 25.00;
saveState();
const balEl = document.getElementById('dom-wallet-bal');
if (balEl) balEl.innerText = $${STATE.user.balance.toFixed(2)};
if (badge) badge.className = "n-badge-status confirmed";
if (spinner) spinner.style.display = "none";
if (txt) txt.innerText = "Transaction Settled via Block Ledger (+$25.00)";
}, 5000);
}
});
function dropModal() {
modal.style.display = 'none';
if (STATE.depositStatus === "confirmed") {
STATE.depositStatus = "idle";
if (badge) badge.className = "n-badge-status";
if (spinner) spinner.style.display = "inline-block";
if (txt) txt.innerText = "Awaiting network transaction broadcast...";
}
}
closeBtn.addEventListener('click', dropModal);
modal.addEventListener('click', (e) => { if (e.target === modal) dropModal(); });
}
// Strict safety latch to wait for window body structure to be completely available
window.addEventListener('load', () => {
STATE = loadPersistedState();
renderLayoutRouter();
});
})();
