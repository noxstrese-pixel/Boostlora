(function() {
    console.log("Boostlora: Self-installer initialized.");

    // Helper function to force-inject the control layout panel into your dashboard window
    function injectBoostModule() {
        // Locate every possible dashboard module slot or window block name inside your application template
        const targets = [
            document.querySelector('.Server.Booster.Module'),
            document.getElementById('boost-module-container'),
            document.querySelector('main'),
            document.querySelector('.content-wrapper'),
            document.body
        ];

        let container = null;
        for (let target of targets) {
            if (target) {
                container = target;
                break;
            }
        }
    
        if (!container) {
            console.error("Boostlora: Could not locate main container slot.");
            return false;
        }

        // Wipe out any default "Not Installed" error text blocks or placeholder buttons cleanly
        container.innerHTML = "";

        // Inject your custom interactive dark slate control panel UI layout
        const style = document.createElement('style');
        style.innerHTML = `
            .boost-wrapper { font-family: system-ui, -apple-system, sans-serif; color: #f3f4f6; max-width: 800px; margin: 0 auto; padding: 20px; }
            .boost-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
            .boost-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; }
            .boost-title { font-size: 20px; font-weight: 600; color: #f3f4f6; margin: 0; }
            .wallet-badge { background: #1e293b; border: 1px solid #334155; border-radius: 20px; padding: 6px 16px; display: flex; align-items: center; gap: 8px; font-size: 14px; }
            .deposit-btn { background: #10b981; color: #fff; border: none; border-radius: 6px; padding: 4px 10px; font-size: 12px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            .deposit-btn:hover { background: #059669; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
            .input-group { display: flex; flex-direction: column; gap: 6px; }
            .input-label { font-size: 13px; color: #9ca3af; font-weight: 500; }
            .input-field { background: #1f2937; border: 1px solid #374151; border-radius: 8px; padding: 10px 14px; color: #fff; font-size: 14px; outline: none; }
            .input-field:focus { border-color: #2563eb; }
            .toggle-container { background: #1f2937; border: 1px solid #374151; border-radius: 8px; display: flex; padding: 4px; }
            .toggle-btn { flex: 1; background: transparent; border: none; color: #9ca3af; padding: 8px; font-size: 13px; font-weight: 500; border-radius: 6px; cursor: pointer; }
            .toggle-btn.active { background: #2563eb; color: #fff; }
            .action-btn { background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 14px; font-size: 15px; font-weight: 600; width: 100%; cursor: pointer; margin-top: 10px; }
            .action-btn:hover { background: #1d4ed8; }
            .status-box { margin-top: 20px; background: #1f2937; border-radius: 8px; padding: 16px; border-left: 4px solid #9ca3af; font-size: 14px; display: none; }
            .status-box.running { border-left-color: #eab308; background: rgba(234,179,8,0.05); }
            .status-box.completed { border-left-color: #10b981; background: rgba(16,185,129,0.05); }
            .status-box.failed { border-left-color: #ef4444; background: rgba(239,68,68,0.05); }
            .counter-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 15px; }
            .counter-card { background: #111827; border: 1px solid #374151; border-radius: 6px; padding: 10px; text-align: center; }
            .counter-num { font-size: 18px; font-weight: bold; margin-bottom: 2px; }
        `;
        document.head.appendChild(style);

        container.innerHTML = `
            <div class="boost-wrapper">
                <div class="boost-card">
                    <div class="boost-header-flex">
                        <h2 class="boost-title">Server Booster Engine</h2>
                        <div class="wallet-badge">
                            <span>Balance: <strong id="wallet-balance">$0.00</strong></span>
                            <button class="deposit-btn" id="deposit-action">Deposit</button>
                        </div>
                    </div>

                    <div class="grid-2">
                        <div class="input-group">
                            <label class="input-label">Execution Mode</label>
                            <div class="toggle-container">
                                <button class="toggle-btn active" id="mode-stock">Store Stock</button>
                                <button class="toggle-btn" id="mode-byot">Your Tokens</button>
                            </div>
                        </div>
                        <div class="input-group">
                            <label class="input-label">Server Invite Link or Code</label>
                            <input type="text" class="input-field" id="boost-invite" placeholder="discord.gg/abc123">
                        </div>
                    </div>

                    <div id="stock-inputs-section">
                        <div class="grid-2">
                            <div class="input-group">
                                <label class="input-label">Number of Boosts</label>
                                <input type="number" class="input-field" id="boost-count" value="2" min="1" max="200">
                            </div>
                            <div class="input-group">
                                <label class="input-label">Product Subscription Option</label>
                                <input type="text" class="input-field" id="boost-product" placeholder="Default Store Stock">
                            </div>
                        </div>
                    </div>

                    <div id="byot-inputs-section" style="display: none;">
                        <div class="input-group" style="margin-bottom: 16px;">
                            <label class="input-label">Paste Custom Tokens (one per line, email:pass:token allowed)</label>
                            <textarea class="input-field" id="boost-tokens-box" rows="5" placeholder="MTk4...&#10;email:pass:token"></textarea>
                        </div>
                    </div>

                    <button class="action-btn" id="submit-boost-task">Launch Boost Sequence</button>

                    <div class="status-box" id="boost-status-panel">
                        <div id="status-title-text" style="font-weight: 600; margin-bottom: 4px;">Job Queue: Idle</div>
                        <div id="status-detail-text" style="color: #9ca3af; font-size: 13px;">Ready to transmit network request.</div>
                        
                        <div class="counter-grid">
                            <div class="counter-card" style="border-bottom: 3px solid #10b981;"><div class="counter-num" id="cnt-delivered" style="color: #10b981;">0</div><div style="font-size: 11px; color:#9ca3af;">Applied</div></div>
                            <div class="counter-card" style="border-bottom: 3px solid #eab308;"><div class="counter-num" id="cnt-requested" style="color: #eab308;">0</div><div style="font-size: 11px; color:#9ca3af;">Target</div></div>
                            <div class="counter-card" style="border-bottom: 3px solid #ef4444;"><div class="counter-num" id="cnt-failed" style="color: #ef4444;">0</div><div style="font-size: 11px; color:#9ca3af;">Failed</div></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Event hooks and variable operational attachments
        let currentMode = 'stock';
        let pollingInterval = null;

        const stockBtn = document.getElementById('mode-stock');
        const byotBtn = document.getElementById('mode-byot');
        const stockSection = document.getElementById('stock-inputs-section');
        const byotSection = document.getElementById('byot-inputs-section');
        const submitBtn = document.getElementById('submit-boost-task');
        const statusPanel = document.getElementById('boost-status-panel');

        stockBtn.addEventListener('click', () => {
            currentMode = 'stock';
            stockBtn.classList.add('active');
            byotBtn.classList.remove('active');
            stockSection.style.display = 'block';
            byotSection.style.display = 'none';
        });

        byotBtn.addEventListener('click', () => {
            currentMode = 'byot';
            byotBtn.classList.add('active');
            stockBtn.classList.remove('active');
            stockSection.style.display = 'none';
            byotSection.style.display = 'block';
        });

        document.getElementById('deposit-action').addEventListener('click', () => {
            const amount = prompt("Enter deposit amount ($):", "5.00");
            if (amount && !isNaN(amount)) {
                alert(`Redirecting to crypto payment gateway invoice for $${parseFloat(amount).toFixed(2)}...`);
                document.getElementById('wallet-balance').innerText = `$${parseFloat(amount).toFixed(2)}`;
            }
        });

        submitBtn.addEventListener('click', async () => {
            const invite = document.getElementById('boost-invite').value.trim();
            if (!invite) {
                alert("Please supply a valid server invitation code.");
                return;
            }

            const bodyData = { mode: currentMode, invite: invite };

            if (currentMode === 'stock') {
                bodyData.boosts = parseInt(document.getElementById('boost-count').value) || 2;
                if (document.getElementById('boost-product').value) {
                    bodyData.product = document.getElementById('boost-product').value;
                }
            } else {
                bodyData.user_tokens_input = document.getElementById('boost-tokens-box').value;
            }

            if (pollingInterval) clearInterval(pollingInterval);
            statusPanel.className = 'status-box running';
            statusPanel.style.display = 'block';
            document.getElementById('status-title-text').innerText = "Status: Transmitting Task...";
            document.getElementById('status-detail-text').innerText = "Connecting to backend function layer...";

            try {
                const res = await fetch('/api/booster', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });

                const data = await res.json();

                if (!res.ok || data.error) {
                    statusPanel.className = 'status-box failed';
                    document.getElementById('status-title-text').innerText = `Error (${res.status})`;
                    document.getElementById('status-detail-text').innerText = data.error || data.details || "Request failed.";
                    return;
                }

                const jobId = data.job_id;
                document.getElementById('status-title-text').innerText = "Status: Job Running...";
                document.getElementById('status-detail-text').innerText = `Tracking ID: ${jobId}`;

                pollingInterval = setInterval(async () => {
                    try {
                        const pollRes = await fetch(`/api/booster_status?job_id=${jobId}`);
                        const job = await pollRes.json();

                        if (!pollRes.ok || job.status === 'completed' || job.status === 'failed') {
                            clearInterval(pollingInterval);
                            statusPanel.className = job.status === 'completed' ? 'status-box completed' : 'status-box failed';
                            document.getElementById('status-title-text').innerText = `Status: ${job.status || 'Finished'}`;
                        }

                        document.getElementById('cnt-delivered').innerText = job.boosts_delivered !== undefined ? job.boosts_delivered : 0;
                        document.getElementById('cnt-requested').innerText = job.boosts_requested !== undefined ? job.boosts_requested : 0;
                        document.getElementById('cnt-failed').innerText = job.failed_count !== undefined ? job.failed_count : 0;

                    } catch (pollErr) {
                        console.error("Polling dropped:", pollErr);
                    }
                }, 8000);

            } catch (err) {
                statusPanel.className = 'status-box failed';
                document.getElementById('status-title-text').innerText = "Connection Failed";
                document.getElementById('status-detail-text').innerText = err.message || "Failed to establish handshake connection loop.";
            }
        });

        return true;
    }

    // Force hook loop to monitor structural creation lifecycle events
    if (!injectBoostModule()) {
        window.addEventListener('DOMContentLoaded', injectBoostModule);
        // Secondary backup listener hooks to clear dynamic layout rendering conflicts
        setTimeout(injectBoostModule, 1000);
        setTimeout(injectBoostModule, 3000);
    }
})();