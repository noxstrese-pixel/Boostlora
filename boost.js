/**
 * Nox Control System Layer
 * Save this file exactly as "boost.js" in the same folder as index.html
 */
(function() {
    console.log("Nox Control Core: Initializing multi-purpose utility framework...");

    // 1. Core State Matrix
    const STATE = {
        user: { 
            balance: 42.50, 
            session_token: "NX_SECURE_77A" 
        },
        activeTab: "booster",
        depositStatus: "idle", // 'idle', 'pending', 'confirmed'
        txTimer: null,
        tools: [
            { id: "checker", name: "Account Checker", status: "Active", icon: "👤", isWip: false },
            { id: "booster", name: "Server Booster", status: "Active", icon: "🚀", isWip: false },
            { id: "joiner", name: "Server Joiner", status: "WIP", icon: "🌐", isWip: true },
            { id: "settings", name: "System Settings", status: "Active", icon: "⚙️", isWip: false }
        ],
        storefront: [
            { id: "p1", title: "1-Month Server Boost Bundle", price: 0.15, stock: 1240, type: "boost", description: "Allocate automated slots to elevate server perks and tier ranks seamlessly." },
            { id: "p2", title: "Premium High-Age Profiles", price: 0.85, stock: 340, type: "account", description: "Aged profile slots populated with randomized realistic avatar media structures." },
            { id: "p3", title: "Profile Management Tool", price: 0.05, stock: 9999, type: "utility", description: "Metadata restructuring assets for cleaning and modifying bulk user data lines." }
        ]
    };

    // 2. Locate Dom Injection Anchor
    const targets = [
        document.querySelector('.Server.Booster.Module'),
        document.getElementById('boost-module-container'),
        document.querySelector('main'),
        document.body
    ];

    let rootElement = null;
    for (let t of targets) { if (t) { rootElement = t; break; } }
    if (!rootElement) {
        console.error("Critical: Could not locate a valid injection root element in the DOM.");
        return;
    }

    // Clear previous elements
    rootElement.innerHTML = "";

    // 3. Inject Visual Engine Stylesheet
    const stylesheet = document.createElement('style');
    stylesheet.innerHTML = `
        :root {
            --bg-deep: #080f19;
            --bg-card: #0f172a;
            --bg-input: #0b1324;
            --border-primary: #1e293b;
            --accent-blue: #2563eb;
            --accent-hover: #1d4ed8;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --success-green: #10b981;
            --warning-amber: #f59e0b;
        }

        .n-dashboard {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-deep);
            color: var(--text-main);
            display: grid;
            grid-template-columns: 260px 1fr;
            min-height: 100vh;
            box-sizing: border-box;
        }

        /* Sidebar Elements */
        .n-sidebar {
            background: var(--bg-card);
            border-right: 1px solid var(--border-primary);
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .n-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 32px;
            padding: 0 8px;
        }
        .n-brand-icon { font-size: 24px; }
        .n-brand-text {
            font-size: 20px;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .n-nav-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .n-nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 10px;
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }
        .n-nav-item:hover {
            background: #1e293b;
            color: #fff;
        }
        .n-nav-item.active {
            background: var(--accent-blue);
            color: #fff;
        }
        .n-wip-badge {
            background: var(--warning-amber);
            color: #000;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: auto;
        }

        /* Wallet Section */
        .n-wallet {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid var(--border-primary);
            padding: 18px;
            border-radius: 14px;
            margin-top: auto;
        }
        .n-wallet-label {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
        }
        .n-wallet-amount {
            font-size: 22px;
            font-weight: 700;
            color: var(--success-green);
            margin: 6px 0 14px 0;
        }
        .n-btn-deposit {
            background: var(--accent-blue);
            color: #fff;
            border: none;
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .n-btn-deposit:hover { background: var(--accent-hover); }

        /* Content Spaces */
        .n-viewport {
            padding: 40px;
            overflow-y: auto;
        }
        .n-view-header {
            margin-bottom: 32px;
        }
        .n-view-title {
            font-size: 26px;
            font-weight: 700;
            margin: 0 0 6px 0;
        }
        .n-view-subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin: 0;
        }

        /* Module Execution Box */
        .n-module-panel {
            background: var(--bg-card);
            border: 1px solid var(--border-primary);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
        }
        .n-field-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 20px;
        }
        .n-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }
        .n-input {
            background: var(--bg-input);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            padding: 14px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .n-input:focus { border-color: var(--accent-blue); }
        .n-btn-execute {
            background: var(--success-green);
            color: #fff;
            font-weight: 700;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            padding: 16px;
            cursor: pointer;
            width: 100%;
            transition: opacity 0.2s;
        }
        .n-btn-execute:hover { opacity: 0.9; }

        /* Catalog Grid Section */
        .n-grid-header {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 18px;
            color: var(--text-main);
        }
        .n-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .n-card {
            background: var(--bg-card);
            border: 1px solid var(--border-primary);
            border-radius: 14px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease;
        }
        .n-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }
        .n-tag {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--accent-blue);
            background: rgba(59, 130, 246, 0.1);
            padding: 4px 8px;
            border-radius: 6px;
            width: max-content;
            margin-bottom: 14px;
        }
        .n-card-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0 0 8px 0;
        }
        .n-card-desc {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 20px;
            flex-grow: 1;
        }
        .n-card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-primary);
            padding-top: 16px;
        }
        .n-price {
            font-size: 16px;
            font-weight: 700;
            color: var(--success-green);
        }
        .n-btn-buy {
            background: #1e293b;
            border: 1px solid #334155;
            color: #fff;
            font-size: 12px;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .n-btn-buy:hover {
            background: var(--accent-blue);
            border-color: var(--accent-blue);
        }

        /* Modernized Gateway Overlay Modal */
        .n-modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(4, 7, 12, 0.85);
            backdrop-filter: blur(8px);
align-items: center;
justify-content: center;
z-index: 99999;
}
.n-modal-box {
background: var(--bg-card);
border: 1px solid var(--border-primary);
border-radius: 24px;
padding: 32px;
max-width: 460px;
width: 100%;
text-align: center;
box-shadow: 0 20px 40px rgba(0,0,0,0.5);
position: relative;
}
.n-modal-close {
position: absolute;
top: 20px; right: 20px;
background: none; border: none;
color: var(--text-muted);
font-size: 20px; cursor: pointer;
}
.n-modal-close:hover { color: #fff; }
.n-address-container {
background: var(--bg-input);
border: 1px solid var(--border-primary);
border-radius: 8px;
font-family: monospace;
font-size: 12px;
padding: 14px;
margin: 16px 0;
color: var(--text-muted);
word-break: break-all;
user-select: all;
}
.n-badge-status {
display: inline-flex;
align-items: center;
gap: 8px;
background: rgba(245, 158, 11, 0.1);
border: 1px solid rgba(245, 158, 11, 0.2);
color: var(--warning-amber);
padding: 8px 20px;
border-radius: 9999px;
font-size: 13px;
font-weight: 600;
}
.n-badge-status.confirmed {
background: rgba(16, 185, 129, 0.1);
border: 1px solid rgba(16, 185, 129, 0.2);
color: var(--success-green);
}
.spinner {
width: 14px; height: 14px;
border: 2px solid currentColor;
border-right-color: transparent;
border-radius: 50%;
animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
`;
document.head.appendChild(stylesheet);
// 4. Structural DOM Shell Layout
const uiShell = document.createElement('div');
uiShell.className = 'n-dashboard';
uiShell.innerHTML = `



🎛️
Nox Control


Available Balance
$42.50
Deposit Crypto

×
Crypto Deposit Gateway
Send funds to the designated address below to credit your account balance.
Dedicated BTC Address
bc1qnx77asecurematrixp99fflowsystem327vpx08cl83a
Awaiting Transaction...




`;
rootElement.appendChild(uiShell);
// 5. Reactive Content Rendering Pipeline
function drawSidebar() {
const menuBox = document.getElementById('dom-nav-menu');
menuBox.innerHTML = "";
STATE.tools.forEach(tool => {
const row = document.createElement('div');
row.className = n-nav-item ${STATE.activeTab === tool.id ? 'active' : ''};
row.innerHTML = <span>${tool.icon}</span> <span>${tool.name}</span>;
if (tool.isWip) {
const badge = document.createElement('span');
badge.className = 'n-wip-badge';
badge.innerText = 'WIP';
row.appendChild(badge);
}
row.addEventListener('click', () => {
if (!tool.isWip) {
STATE.activeTab = tool.id;
drawSidebar();
drawViewport();
}
});
menuBox.appendChild(row);
});
}
function drawViewport() {
const view = document.getElementById('dom-workspace-viewport');
view.innerHTML = "";
if (STATE.activeTab === "booster") {
view.innerHTML = `

Server Booster Module
Configure data deployment parameters and tool metrics below.
Target Multi-Guild Invite Link
Quantity Amount Selection
Deploy Modification Parameters
Available Procurement Catalog

`;
// Build Store Grid Inside Module View
const storeBox = document.getElementById('dom-catalog-box');
STATE.storefront.forEach(item => {
const card = document.createElement('div');
card.className = 'n-card';
card.innerHTML = <div> <div class="n-tag">${item.type}</div> <h4 class="n-card-title">${item.title}</h4> <p class="n-card-desc">${item.description}</p> </div> <div class="n-card-footer"> <div class="n-price">$${item.price.toFixed(2)}</div> <button class="n-btn-buy">Purchase Asset</button> </div>;
card.querySelector('.n-btn-buy').addEventListener('click', () => {
if (STATE.user.balance >= item.price) {
STATE.user.balance -= item.price;
document.getElementById('dom-wallet-bal').innerText = $${STATE.user.balance.toFixed(2)};
alert(Successfully unlocked item: ${item.title});
} else {
alert("Insufficient system balance metrics. Please credit your balance via the deposit gateway.");
}
});
storeBox.appendChild(card);
});
// Action Binding
document.getElementById('btn-run-booster').addEventListener('click', () => {
const lnk = document.getElementById('input-target-link').value;
if (!lnk) {
alert("Please provide a valid destination tracking handle or invite parameter.");
return;
}
alert("Process sequence initiated using available state inventory configs.");
});
} else {
const activeTool = STATE.tools.find(t => t.id === STATE.activeTab);
view.innerHTML = <div class="n-view-header"> <h2 class="n-view-title">${activeTool.name}</h2> <p class="n-view-subtitle">System metrics tracking layer variables.</p> </div> <div class="n-module-panel"> <p style="color:var(--text-muted); font-size:14px; margin:0;">Platform subsystem component online and ready.</p> </div>;
}
}
// 6. Blockchain Simulation Interface Layer
function configureGatewayInteractions() {
const modal = document.getElementById('dom-deposit-modal');
const openBtn = document.getElementById('dom-open-deposit-btn');
const closeBtn = document.getElementById('dom-close-modal-btn');
const badge = document.getElementById('dom-modal-status-badge');
const spinner = document.getElementById('dom-modal-spinner');
const txt = document.getElementById('dom-modal-status-text');
openBtn.addEventListener('click', () => {
modal.style.display = 'flex';
if (STATE.depositStatus === "idle") {
STATE.depositStatus = "pending";
txt.innerText = "Scanning ledger for network confirmation...";
// Simulate Asynchronous Ledger Block Confirmation Wait Sequence
STATE.txTimer = setTimeout(() => {
STATE.depositStatus = "confirmed";
STATE.user.balance += 25.00; // Crediting state balance metrics
document.getElementById('dom-wallet-bal').innerText = $${STATE.user.balance.toFixed(2)};
badge.className = "n-badge-status confirmed";
spinner.style.display = "none";
txt.innerText = "Block Confirmation Verified (+$25.00)";
}, 5000); // 5-second mock ledger ingestion period
}
});
function dropModal() {
modal.style.display = 'none';
// Reset simulation pipeline state when modal closes
if (STATE.depositStatus === "confirmed") {
STATE.depositStatus = "idle";
badge.className = "n-badge-status";
spinner.style.display = "inline-block";
txt.innerText = "Awaiting Transaction...";
}
}
closeBtn.addEventListener('click', dropModal);
modal.addEventListener('click', (e) => { if (e.target === modal) dropModal(); });
}
// Initialize UI Component Flow
drawSidebar();
drawViewport();
configureGatewayInteractions();
})();
