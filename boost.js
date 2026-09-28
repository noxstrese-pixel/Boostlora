/**
 * Boostlora Dashboard Control Engine v16.2
 */
console.log("Boostlora Core: Initializing dashboard systems...");

// Tab View Router Engine (Unblocked Mouse Interactions)
function switchView(viewName, element) {
    // Hide all panels
    document.querySelectorAll('.view-panel').forEach(p => {
        p.classList.remove('active');
    });
    
    // Clear active highlight styles from all menu blocks
    document.querySelectorAll('.nav-item').forEach(i => {
        i.classList.remove('active');
    });
    
    // Mount the target workspace module window
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.add('active');
    }
    
    // Attach current highlight accent onto active menu node
    if (element) {
        element.classList.add('active');
    }
}

// Controls visibility state for custom token text fields
function toggleTokenInput() {
    const strategyElement = document.getElementById('token-source');
    const tokensWrapper = document.getElementById('custom-tokens-wrapper');
    const tokensField = document.getElementById('custom-tokens-field');
    
    if (!strategyElement || !tokensWrapper || !tokensField) return;

    if (strategyElement.value === 'custom') {
        tokensWrapper.style.display = 'block';
        tokensField.setAttribute('required', 'true');
    } else {
        tokensWrapper.style.display = 'none';
        tokensField.removeAttribute('required');
    }
}

// Live Cost Calculator for Order Invoicing
function calculateBoostCost() {
    const strategyElement = document.getElementById('token-source');
    const amountElement = document.getElementById('boost-amount');
    const displayElement = document.getElementById('boost-cost-display');

    if (!strategyElement || !amountElement || !displayElement) return;

    const strategy = strategyElement.value;
    const amount = parseInt(amountElement.value) || 0;
    let totalCost = 0;

    if (strategy === 'salta7') {
        totalCost = amount * 0.18; // Reseller profit tier metric (\$0.18)
    } else if (strategy === 'custom') {
        totalCost = amount * 0.02; // Custom tokens processing rate (\$0.02)
    }

    displayElement.innerText = `$${totalCost.toFixed(2)} USD`;
}

// Clean Vercel Backend API Connection Handler with Live Logs Feed
async function handleApiAction(event, endpoint) {
    event.preventDefault();
    
    const currentForm = event.target;
    const inputData = currentForm.querySelector('input[type="text"]')?.value || currentForm.querySelector('textarea')?.value || "";
    const amountData = currentForm.querySelector('input[type="number"]')?.value || "";
    const strategyData = document.getElementById('token-source')?.value || "salta7";
    const customTokensData = document.getElementById('custom-tokens-field')?.value || "";

    let loggerBox = currentForm.querySelector('.live-logger-terminal');
    if (!loggerBox) {
        loggerBox = document.createElement('div');
        loggerBox.className = 'live-logger-terminal';
        loggerBox.style = "background:#020408; border:1px solid #1a2642; border-radius:8px; padding:12px; margin-top:16px; font-family:monospace; font-size:12px; color:#38bdf8; max-height:200px; overflow-y:auto; text-align:left; line-height:1.6;";
        currentForm.appendChild(loggerBox);
    }
    
    loggerBox.innerHTML = "<div style='color:#64748b;'>[System] Initializing connection to Vercel API runner...</div>";

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                input: inputData,
                amount: amountData,
                strategy: strategyData,
                custom_tokens: customTokensData,
                trigger: "active" 
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            loggerBox.innerHTML += `<div>${chunk}</div>`;
            loggerBox.scrollTop = loggerBox.scrollHeight;
        }
        
        loggerBox.innerHTML += "<div style='color:#10b981; font-weight:bold; margin-top:6px;'>[Finished] All pipeline tasks handled completely.</div>";
    } catch (err) {
        console.error("API Pipeline Error: ", err);
        loggerBox.innerHTML += "<div style='color:#ef4444;'>[Error] Connection failed to parse backend stream.</div>";
    }
}

// Crypto Invoicing Launcher Engine with Strict Minimum Bound Metrics
function triggerPayment() {
    const amountElement = document.getElementById('deposit-amount');
    const amount = amountElement ? parseFloat(amountElement.value) : 0;

    // Strict validation safety catch limit layer rule
    if (isNaN(amount) || amount < 1.00) {
        alert("Invoice Generation Canceled: The minimum deposit required on Boostlora is \$1.00 USD.");
        return;
    }

    if (window.Clerk && !window.Clerk.user) {
        alert("Please connect an account profile to log this invoice securely.");
        window.Clerk.openSignIn();
        return;
    }
    
    const userId = window.Clerk.user ? window.Clerk.user.id : "guest_session";
    const userEmail = window.Clerk.user ? window.Clerk.user.primaryEmailAddress.emailAddress : "no_email";
    
    // Once you generate your unique Checkout ID key in Coinbase Commerce, drop it here!
    const commerceUrl = `https://coinbase.com{amount}&custom=${userId}&email=${userEmail}`;
    window.open(commerceUrl, '_blank', 'width=500,height=700,status=yes,resizable=yes');
}

// Authentication Loader Initialization Loop
window.addEventListener('load', async function() {
    const script = document.getElementById('clerk-script');
    if (!script) return;

    script.addEventListener('load', async function() {
        if (!window.Clerk) return;
        await window.Clerk.load();
        
        const authButtons = document.getElementById('auth-buttons');
        const profileSlot = document.getElementById('user-profile-slot');
        const signInBtn = document.getElementById('sign-in-btn');

        if (window.Clerk.user) {
            window.Clerk.mountUserButton(profileSlot, { appearance: { baseTheme: 'dark' } });
            if (authButtons) authButtons.style.display = 'none';
        } else {
            if (authButtons) authButtons.style.display = 'block';
            if (signInBtn) {
                signInBtn.addEventListener('click', () => { window.Clerk.openSignIn(); });
            }
        }
    });
});
