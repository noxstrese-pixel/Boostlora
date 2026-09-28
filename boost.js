/**
 * Nox Control System Layer v6.0 - Structural Native Fix
 * Save this file exactly as "boost.js" in the same folder as index.html
 */
(function() {
    console.log("Nox Control Core: Launching dashboard engine lifecycle...");

    const STORAGE_KEY = "NOX_CENTRAL_PERSISTENCE_V6";
    let STATE = null;
    let txTimer = null;
    let rootElement = null;

    function loadPersistedState() {
        const fallbackDefault = {
            isLoggedIn: false,
            user: { username: "", balance: 0.00, session_token: "" },
            activeTab: "checker",
            depositStatus: "idle",
            storefront: [
                { id: "p1", title: "1-Month Boost Slot", price: 0.15, type: "boost", description: "Allocate automated tokens to elevate targeted servers." },
                { id: "p2", title: "Premium High-Age Profile", price: 0.85, type: "account", description: "Aged profiles populated with realistic media records." },
                { id: "p3", title: "Profile Management Tool", price: 0.05, type: "utility", description: "Metadata restructuring script for bulk user management." }
            ]
        };

        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return fallbackDefault;
            const parsed = JSON.parse(raw);
            parsed.storefront = fallbackDefault.storefront;
            parsed.depositStatus = "idle"; 
            return parsed;
        } catch (e) {
            return fallbackDefault;
        }
    }

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(STATE));
    }

    function buildWorkspaceEnvironment() {
        rootElement = document.getElementById('app-mount-root');
        if (!rootElement) {
            console.error("Critical Failure: Mount node missing.");
            return;
        }

        STATE = loadPersistedState();
        renderLayoutRouting();
    }

    function renderLayoutRouting() {
        rootElement.innerHTML = "";

        if (!STATE.isLoggedIn) {
            // Render Clean Interface Portal Module Login Layout Frame
            rootElement.innerHTML = `
                <div class="n-auth-screen">
                    <div class="n-auth-card">
                        <h3 style="margin: 0 0 6px 0; font-size: 20px; font-weight: 800; text-align: center;">System Portal Access</h3>
                        <p style="margin: 0 0 24px 0; font-size: 13px; color: var(--text-muted); text-align: center;">Provide a workspace handle identity to resume credit cache balances.</p>
                        <div style="margin-bottom: 20px;">
                            <label style="font-size: 12px; font-weight:600; color: var(--text-muted); display:block; margin-bottom:6px;">Account Username</label>
                            <input type="text" class="n-input" id="auth-username-field" placeholder="Username entry..." />
                        </div>
                        <button class="action-btn" id="auth-submit-btn">Initialize Connection Profile</button>
                    </div>
                </div>
            `;

            document.getElementById('auth-submit-btn').addEventListener('click', () => {
                const userVal = document.getElementById('auth-username-field').value.trim();
                if (!userVal) {
                    alert("A valid credential handle string must be specified.");
                    return;
                }
                STATE.isLoggedIn = true;
                STATE.user.username = userVal;
                if (STATE.user.balance === 0) {
                    STATE.user.balance = 42.50;
                    STATE.user.session_token = "NX_" + Math.random().toString(36).substring(2, 6).toUpperCase();
                }
                saveState();
                renderLayoutRouting();
            });
            return;
        }

        // Render Comprehensive Split Interface Sidebar Core Workspace Layout Shell Matrix
        rootElement.innerHTML = `
            <aside class="sidebar">
                <div class="sidebar-brand">Boostlora</div>
                <button class="nav-btn ${STATE.activeTab === 'checker' ? 'active' : ''}" id="nav-tab-checker" type="button">Account Checker</button>
                <button class="nav-btn ${STATE.activeTab === 'booster' ? 'active' : ''}" id="nav-tab-booster" type="button">Server Booster <span class="badge-dev">WIP</span></button>
                <button class="nav-btn ${STATE.activeTab === 'joiner' ? 'active' : ''}" id="nav-tab-joiner" type="button">Server Joiner <span class="badge-dev">WIP</span></button>
                
                <div class="sidebar-wallet">
                    <div class="wallet-title">User Account: <span style="color:#fff;">${STATE.user.username}</span></div>
                    <div class="wallet-title">System Balance</div>
                    <div class="wallet-amount" id="dom-wallet-bal">$${STATE.user.balance.toFixed(2)}</div>
                    <button class="wallet-btn" id="dom-open-deposit-btn">Deposit Crypto</button>
                    <button class="wallet-btn-logout" id="dom-logout-btn">Log Out Session</button>
                </div>
            </aside>

            <main class="content-area">
                <div class="dashboard-container" id="dom-panel-viewport"></div>
            </main>

            <div class="n-modal-overlay" id="dom-deposit-modal">
                <div class="n-modal-box">
                    <button class="n-modal-close" id="dom-close-modal-btn">×</button>
                    <h3 style="margin:0 0 8px 0; font-size:18px; font-weight:800;">Crypto Ledger Pipeline Gateway</h3>
                    <p style="font-size:13px; color:var(--text-muted); margin:0;">Provision immediate system cache credits down through automated mempool verification routes.</p>
                    <div class="wallet-title" style="text-align:left; margin-top:20px;">Dedicated Account Token BTC Destination</div>
                    <div class="n-address-container">bc1qnx77asecurematrixp99fflowsystem327vpx08cl83a</div>
                    <div style="margin-top:24px;">
                        <div class="n-badge-status" id="dom-modal-status-badge">
                            <div class="spinner" id="dom-modal-spinner"></div>
                            <span id="dom-modal-status-text">Awaiting network payload broadcast...</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Attach Core Sidebar Command Controls Logic Elements
        document.getElementById('nav-tab-checker').addEventListener('click', () => switchTab('checker'));
        document.getElementById('nav-tab-booster').addEventListener('click', () => switchTab('booster'));
        document.getElementById('nav-tab-joiner').addEventListener('click', () => switchTab('joiner'));
        
        document.getElementById('dom-logout-btn').addEventListener('click', () => {
            STATE.isLoggedIn = false;
            saveState();
            renderLayoutRouting();
        });

        drawActiveViewportPanel();
        configureGatewayInteractions();
    }

    function switchTab(tabId) {
        STATE.activeTab = tabId;
        saveState();
        renderLayoutRouting();
    }

    function drawActiveViewportPanel() {
        const view = document.getElementById('dom-panel-viewport');
        if (!view) return;
        view.innerHTML = "";

        if (STATE.activeTab === "checker") {
            view.innerHTML = `
                <div class="header-section">
                    <h2>Account Checker Subsystem Matrix</h2>
                    <p class="subtitle">Input raw parameter sequence text strings below to scan performance layout metrics variables.</p>
                </div>
                <textarea placeholder="Paste account token configurations here (one entry per line parameter combo)..."></textarea>
                <button class="action-btn">Launch System Verification Check Pipeline</button>
                
                <div class="results-section">
                    <div class="status-title">Ecosystem Performance Logging Parameters</div>
                    <div class="stats-grid">
                        <div class="grid-item valid"><div class="stat-val">0</div><div class="stat-label">Verified Valid</div></div>
                        <div class="grid-item warning"><div class="stat-val">0</div><div class="stat-label">Flagged Flag</div></div>
                        <div class="grid-item invalid"><div class="stat-val">0</div><div class="stat-label">Rejected Bad</div></div>
                    </div>
                    <div class="list-container" style="padding:40px; text-align:center; color:var(--text-muted); font-size:13px;">
                        Awaiting check execution parameters payload queue submission...
                    </div>
                </div>
            `;
        } else if (STATE.activeTab === "booster") {
            view.innerHTML = `
                <div class="header-section">
                    <h2>Server Booster Allocation Framework <span class="badge-dev" style="float:none; margin-left:6px;">WIP</span></h2>
                    <p class="subtitle">Provision structural tier optimization slots dynamically down to destination assets.</p>
                </div>
                <div class="module-box" style="background: var(--bg-main); border: 1px solid var(--border-color); padding: 24px; text-align:left; border-radius:12px; margin-bottom:24px;">
                    <div style="margin-bottom:16px;">
                        <label style="font-size:12px; font-weight:600; color:var(--text-muted); display:block; margin-bottom:6px;">Target Invite Code Link Location</label>
                        <input type="text" class="n-input" placeholder="https://discord.gg" id="booster-lnk-input" />
                    </div>
Deploy Configuration Allocation Bundle
Available Resource Inventory Procurement Procurement

`;
const storeBox = document.getElementById('dom-store-box');
STATE.storefront.forEach(item => {
const card = document.createElement('div');
card.className = 'store-card';
card.innerHTML = <div> <h4 class="store-title">${item.title}</h4> <p class="store-desc">${item.description}</p> </div> <div class="store-footer"> <div class="store-price">$${item.price.toFixed(2)}</div> <button class="store-btn">Unlock Asset</button> </div>;
card.querySelector('.store-btn').addEventListener('click', () => {
if (STATE.user.balance >= item.price) {
STATE.user.balance -= item.price;
saveState();
document.getElementById('dom-wallet-bal').innerText = $${STATE.user.balance.toFixed(2)};
alert(Successfully added credit procurement asset line: ${item.title});
} else {
alert("Insufficient available system balance credits inside current profile context.");
}
});
storeBox.appendChild(card);
});
document.getElementById('booster-exec-btn').addEventListener('click', () => {
const txt = document.getElementById('booster-lnk-input').value;
if (!txt) { alert("Please provide a valid server target identity string."); return; }
alert("Allocation array tracking variables initialized cleanly.");
});
} else {
view.innerHTML = <div class="header-section"> <h2>Server Joiner Module <span class="badge-dev" style="float:none; margin-left:6px;">WIP</span></h2> <p class="subtitle">System framework development sandbox layer configuration space tools.</p> </div> <div style="padding:60px; text-align:center; border: 1px dashed var(--border-color); border-radius:12px; color:var(--text-muted); font-size:13px;"> Subsystem module layer variables are currently deploying under active dev tracking profiles. </div>;
}
}
function configureGatewayInteractions() {
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
if (txt) txt.innerText = "Awaiting network payload broadcast...";
}
}
closeBtn.addEventListener('click', dropModal);
modal.addEventListener('click', (e) => { if (e.target === modal) dropModal(); });
}
if (document.readyState === "complete" || document.readyState === "interactive") {
buildWorkspaceEnvironment();
} else {
document.addEventListener("DOMContentLoaded", buildWorkspaceEnvironment);
}
})();
