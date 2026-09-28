(function() {
    console.log("Platform Core: Initializing multi-purpose utility framework...");

    // Central Platform Configuration Matrix
    const PLATFORM_DATABASE = {
        user: { balance: 42.50, session_token: "NX_SECURE_77A" },
        tools: [
            { id: "checker", name: "Account Checker", status: "Active", icon: "👤" },
            { id: "booster", name: "Server Booster", status: "Active", icon: "🚀" },
            { id: "joiner", name: "Server Joiner", status: "WIP", icon: "🌐" },
            { id: "settings", name: "System Settings", status: "Active", icon: "⚙️" }
        ],
        storefront: [
            { id: "p1", title: "1-Month Server Boost", price: 0.15, stock: 1240, type: "boost", description: "Instantly deploy tokens to elevate guild perks tier ranks." },
            { id: "p2", title: "Premium Nitro Account", price: 0.85, stock: 340, type: "account", description: "High-age tokens equipped with random avatar media profiles." },
            { id: "p3", title: "Custom Profile Humanizer", price: 0.05, stock: 9999, type: "utility", description: "Automated profile metadata restructuring asset pipeline." }
        ]
    };

    function renderPlatformLayout() {
        const targets = [
            document.querySelector('.Server.Booster.Module'),
            document.getElementById('boost-module-container'),
            document.querySelector('main'),
            document.body
        ];

        let targetRoot = null;
        for (let t of targets) { if (t) { targetRoot = t; break; } }
        if (!targetRoot) return false;

        targetRoot.innerHTML = "";

        // Global Platform Workspace Stylesheet Configuration Map
        const style = document.createElement('style');
        style.innerHTML = `
            .p-workspace { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0b131f; color: #f3f4f6; display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }
            .p-sidebar { background: #0f172a; border-right: 1px solid #1e293b; padding: 24px 16px; display: flex; flex-direction: column; justify-content: space-between; }
            .p-brand-container { display: flex; align-items: center; gap: 12px; margin-bottom: 32px; padding: 0 8px; }
            .p-brand-text { font-size: 20px; font-weight: 800; background: linear-gradient(135deg, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            
            .p-menu { display: flex; flex-direction: column; gap: 8px; }
            .p-menu-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; color: #9ca3af; font-size: 14px; font-weight: 600; cursor: pointer; transition: 0.2s; text-decoration: none; }
            .p-menu-item:hover, .p-menu-item.active { background: #1e293b; color: #fff; }
            .p-menu-item .wip-badge { background: #f59e0b; color: #0f172a; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: auto; }
            
            .p-wallet-card { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; padding: 16px; border-radius: 12px; margin-top: auto; }
            .p-wallet-bal { font-size: 18px; font-weight: 700; color: #10b981; margin: 4px 0 12px 0; }
            .p-wallet-btn { background: #2563eb; color: #fff; border: none; width: 100%; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
            .p-wallet-btn:hover { background: #1d4ed8; }
            
            .p-content { padding: 40px; overflow-y: auto; max-width: 1200px; width: 100%; box-sizing: border-box; }
            .p-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
            .p-title { font-size: 24px; font-weight: 700; margin: 0; color: #fff; }
            
            .store-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
            .store-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, border-color 0.2s; }
            .store-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
            .store-tag { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #3b82f6; background: rgba(59,130,246,0.1); padding: 4px 8px; border-radius: 6px; width: max-content; margin-bottom: 12px; }
            .store-title { font-size: 16px; font-weight: 600; margin: 0 0 8px 0; color: #fff; }
            .store-desc { font-size: 13px; color: #9ca3af; line-height: 1.4; margin-bottom: 16px; flex-grow: 1; }
            .store-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #1e293b; padding-top: 14px; }
            .store-price { font-size: 16px; font-weight: 700; color: #10b981; }
            .store-btn { background: #1e293b; border: 1px solid #334155; color: #fff; font-size: 12px; font-weight: 600; padding: 8px 14px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
            .store-btn:hover { background: #3b82f6; border-color: #3b82f6; }
            
            /* Legacy Integration Card Module Injection Wrapper Styles */
            .tool-box-wrapper { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 28px; }
            .input-box { display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px; }
            .input-ctrl { background: #0b131f; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; color: #fff; outline: none; }
            .input-ctrl:focus { border-color: #3b82f6; }
            .action-btn { background: #2563eb; color: #fff; font-weight: 600; border: none; border-radius: 8px; padding: 14px; cursor: pointer; width: 100%; transition: 0.2s; }
            .action-btn:hover { background: #1d4ed8; }
            
            /* Blockchain Verification Modal Sheet Overlay */
            .c-modal { display: none; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(6px); align-items:center; justify-content:center; z-index:99999; }
            .c-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 24px; padding: 32px; max-width: 440px; width: 100%; text-align: center; }
            .c-qrcode-box { background: #fff; width: 150px; height: 150px; margin: 24px auto; border-radius: 12px; padding: 12px; display: flex; align-items: center; justify-content: center; }
            .c-address-row { background: #0b131f; border: 1px solid #1e293b; border-radius: 8px; font-family: monospace; font-size: 11px; padding: 12px; margin: 16px 0; color: #9ca3af; word-break: break-all; text-align: center; user-select: all; }
            .c-status { display: inline-flex; align-items: center; gap: 8px; background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2); color: #f59e0b; padding: 8px 18px; border-radius: 9999px; font-size: 13px; font-weight: 600; }
            .c-status.confirmed { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); color: #10b981; }
        `;
        document.head.appendChild(style);

        // Inject Global Split Dashboard Window Elements
        targetRoot.innerHTML = `
            <div class="p-workspace">
                <div class="p-sidebar">
                    <div>
                        <div class="p-brand-container">
                            <div style="font-size:24px;">🎛️</div>
                            <div class="p-brand-text">Nox Control</div>
                        </div>
                        <div class="p-menu" id="sidebar-menu-list"></div>
                    </div>
                    
                    <div class="p-wallet-card">
                        <div style="font-size:12px; color:#9ca3af; font-weight:500;">Available Credit Balance</div>
                        <div class="p-wallet-bal" id="lbl-sidebar-bal">$42.50</div>
                        <button class="p-wallet-btn" id="btn-open-deposit">Deposit Crypto</button>
                    </div>
                </div>
                
                <div class="p-content">
                    <div class="p-header">
                        <h1 class="p-title" id="lbl-workspace-title">Platform Storefront</h1>
                        <div style="font-size:13px; color:#6b7280; font-weight:500;" id="lbl-workspace-date">System Stable</div>
                    </div>
                    <div id="workspace-view-panel"></div>
                </div>
            </div>

            <!-- Ledger Merchant Modal Box Window -->
            <div class="c-modal" id="p-payment-modal">
                <div class="c-card">
                    <h3 style="margin:0; color:#fff; font-size:18px;">Merchant Network Invoice</h3>
                    <p style="font-size: 13px; color:#9ca3af; margin:4px 0 0 0;">Automated Non-Custodial Multi-Chain Verification</p>
                    
                    <div class="c-qrcode-box">
                        <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#0f172a" stroke-width="1.5"><path d="M3 3h6v6H3V3zm12 0h6v6h-6V3zM3 15h6v6H3v-6zm14 2h2v2h-2v-2zm-2-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 0h2v2h-2v-2zM7 7h-2v-2h2v2zm12 0h-2v-2h2v2zM7 19h-2v-2h2v2z"/></svg>
                    </div>
                    
                    <div style="font-size: 20px; font-weight: 800; color:#fff;" id="lbl-crypto-cost">0.082 LTC</div>
                    <div class="c-address-row" id="lbl-crypto-address">LbcTx7PFaK8M82PnHXmZW6ZHNydMYMDY4MjNXU3...</div>
                    
                    <div class="c-status" id="lbl-payment-state">
                        <span id="lbl-payment-text">Awaiting Mempool Broadcast...</span>
                    </div>
Cancel Billing Request


`;
// Render Application Sidebar Elements Array Lists
const menuContainer = document.getElementById('sidebar-menu-list');
// Add dynamic main store tab option control header entry link
const storeLink = document.createElement('div');
storeLink.className = "p-menu-item active";
storeLink.innerHTML = <span>🏪</span> Store Marketplace;
storeLink.addEventListener('click', () => switchView('store', storeLink));
menuContainer.appendChild(storeLink);
PLATFORM_DATABASE.tools.forEach(tool => {
const item = document.createElement('div');
item.className = "p-menu-item";
item.innerHTML = <span>${tool.icon}</span> ${tool.name};
if(tool.status === 'WIP') { item.innerHTML += <span class="wip-badge">WIP</span>; }
item.addEventListener('click', () => switchView(tool.id, item));
menuContainer.appendChild(item);
});
// Interface Navigation Router Switch Logic Matrix Mapping
function switchView(viewId, elementClicked) {
document.querySelectorAll('.p-menu-item').forEach(el => el.classList.remove('active'));
elementClicked.classList.add('active');
const title = document.getElementById('lbl-workspace-title');
const panel = document.getElementById('workspace-view-panel');
panel.innerHTML = "";
if(viewId === 'store') {
title.innerText = "Platform Storefront";
panel.innerHTML = <div class="store-grid" id="store-catalog-target"></div>;
renderStoreCatalog();
} else if(viewId === 'booster') {
title.innerText = "Server Booster Engine";
panel.innerHTML = <div class="tool-box-wrapper"> <div class="input-box"><label class="input-label">Invite Link</label><input type="text" class="input-ctrl" id="b-invite" placeholder="discord.gg/abc"></div> <div class="input-box"><label class="input-label">Quantity</label><input type="number" class="input-ctrl" id="b-count" value="2"></div> <button class="action-btn" id="b-submit">Initialize Stock Boost Pipeline</button> </div>;
document.getElementById('b-submit').addEventListener('click', () => alert("Connecting booster task parameters..."));
} else {
title.innerText = ${viewId.toUpperCase()} Workspace;
panel.innerHTML = <div style="background:#0f172a; border:1px dashed #1e293b; padding:40px; text-align:center; border-radius:12px; color:#4b5563; font-size:14px;">Module view layer structure slot ready for custom script implementation blocks.</div>;
}
}
// Render Dynamic Catalog Storefront Product Cards Layout
function renderStoreCatalog() {
const target = document.getElementById('store-catalog-target');
if(!target) return;
PLATFORM_DATABASE.storefront.forEach(prod => {
const card = document.createElement('div');
card.className = "store-card";
card.innerHTML = <div> <div class="store-tag">${prod.type}</div> <h4 class="store-title">${prod.title}</h4> <p class="store-desc">${prod.description}</p> </div> <div class="store-footer"> <span class="store-price">$${prod.price.toFixed(2)} <span style="font-size:11px; color:#4b5563; font-weight:normal;">/ unit</span></span> <button class="store-btn" data-id="${prod.id}">Purchase</button> </div>;
target.appendChild(card);
});
}
// Blockchain Transaction Mempool Monitoring Simulation Engine
document.getElementById('btn-open-deposit').addEventListener('click', () => {
const modal = document.getElementById('p-payment-modal');
const stateText = document.getElementById('lbl-payment-text');
const statePill = document.getElementById('lbl-payment-state');
modal.style.display = "flex";
statePill.className = "c-status";
stateText.innerText = "Awaiting Blockchain Network Broadcast...";
// Simulation Step 1: Detect transaction inside decentralized nodes
setTimeout(() => {
if(modal.style.display === 'flex') {
stateText.innerText = "Mempool Unconfirmed Hash Detected: Confirming (0/1)...";
}
}, 4000);
// Simulation Step 2: Confirm block execution ledger write and dispatch balance tokens
setTimeout(() => {
if(modal.style.display === 'flex') {
statePill.className = "c-status confirmed";
stateText.innerText = "Ledger Confirmed! Credit Balance Synchronized.";
PLATFORM_DATABASE.user.balance += 10.00;
document.getElementById('lbl-sidebar-bal').innerText = $${PLATFORM_DATABASE.user.balance.toFixed(2)};
setTimeout(() => { modal.style.display = "none"; }, 1500);
}
}, 9500);
});
document.getElementById('btn-close-payment').addEventListener('click', () => {
document.getElementById('p-payment-modal').style.display = "none";
});
// Initialize First View State Layout Content Card Rendering Automatically
switchView('store', storeLink);
return true;
}
if (!renderPlatformLayout()) {
window.addEventListener('DOMContentLoaded', renderPlatformLayout);
setTimeout(renderPlatformLayout, 400);
setTimeout(renderPlatformLayout, 2500);
}
})();
