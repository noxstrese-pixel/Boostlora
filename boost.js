/**
 * Boostlora Dashboard Control Engine v16.0
 */
console.log("Boostlora Core: Initializing dynamic framework engines...");

// Tab View Router Engine
// Tab View Router Engine (Fixed Event-Handling Protocol)
function switchView(viewName, element) {
    // Hide all view panels safely
    document.querySelectorAll('.view-panel').forEach(p => {
        p.classList.remove('active');
    });
    
    // Remove active glowing styles from all menu option blocks
    document.querySelectorAll('.nav-item').forEach(i => {
        i.classList.remove('active');
    });
    
    // Reveal the chosen workspace window
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.add('active');
    }
    
    // Apply the active glow indicator directly onto the clicked tab element
    if (element) {
        element.classList.add('active');
    } else if (window.event && window.event.currentTarget) {
        window.event.currentTarget.classList.add('active');
    }
}
    if (strategy === 'custom') {
        tokensWrapper.style.display = 'block';
        tokensField.setAttribute('required', 'true');
    } else {
        tokensWrapper.style.display = 'none';
        tokensField.removeAttribute('required');
    }
}

// Dynamic Cost Calculator Engine for Server Booster Grid
function calculateBoostCost() {
    const strategyElement = document.getElementById('token-source');
    const amountElement = document.getElementById('boost-amount');
    const displayElement = document.getElementById('boost-cost-display');

    if (!strategyElement || !amountElement || !displayElement) return;

    const strategy = strategyElement.value;
    const amount = parseInt(amountElement.value) || 0;
    let totalCost = 0;

    if (strategy === 'salta7') {
        totalCost = amount * 2.50; // White-labeled premium price marker
    } else if (strategy === 'custom') {
        totalCost = amount * 0.02; // Captcha network processing fee rate
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
                custom_tokens: customTokensData, // Safely forwards their tokens to your api
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

// Crypto Invoicing Launcher Engine
function triggerPayment() {
    const amountElement = document.getElementById('deposit-amount');
    const amount = amountElement ? amountElement.value : "25";

    if (window.Clerk && !window.Clerk.user) {
        alert("Please connect an account profile to log this invoice securely.");
        window.Clerk.openSignIn();
        return;
    }
    
    const userId = window.Clerk.user.id;
    const userEmail = window.Clerk.user.primaryEmailAddress.emailAddress;
    
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
