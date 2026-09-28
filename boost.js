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
