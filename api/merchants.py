"""
Merchant API - Discover and interact with local businesses accepting AT
"""

def register_merchant_routes(router, ledger, auth_decorator):
    """Register merchant discovery and profile endpoints"""
    
    @router.get('/api/merchants')
    def list_merchants(handler):
        """Get all active merchants accepting AT"""
        merchants = ledger.query(
            "SELECT * FROM merchants WHERE accepts_at = 1 AND status = 'active'"
        )
        handler.send_json({"merchants": merchants})
    
    @router.get('/api/merchants/<merchant_id>')
    def get_merchant(handler, merchant_id):
        """Get detailed merchant profile"""
        merchant = ledger.query_one(
            "SELECT * FROM merchants WHERE merchant_id = ?", 
            (merchant_id,)
        )
        if not merchant:
            return handler.send_error("Merchant not found", status=404)
        
        # Get services/products
        services = ledger.query(
            "SELECT * FROM merchant_services WHERE merchant_id = ?",
            (merchant_id,)
        )
        
        merchant['services'] = services
        handler.send_json({"merchant": merchant})
    
    @router.post('/api/merchants/onboard')
    @auth_decorator
    def onboard_merchant(handler, payload):
        """Onboard a new merchant (admin or self-service)"""
        user = handler.get_auth_user()
        
        required = ['name', 'category', 'description']
        if not all(k in payload for k in required):
            return handler.send_error("Missing required fields")
        
        merchant_id = f"{payload['category']}_{payload['name'].lower().replace(' ', '_')}"
        
        # Insert merchant
        ledger.execute("""
            INSERT INTO merchants (
                merchant_id, name, owner_wallet, category, 
                description, accepts_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            merchant_id,
            payload['name'],
            user['wallet_id'],
            payload['category'],
            payload['description'],
            payload.get('accepts_at', True),
            'active'
        ))
        
        # Insert services
        for service in payload.get('services', []):
            ledger.execute("""
                INSERT INTO merchant_services (
                    merchant_id, name, price_at, price_usd, 
                    description, duration_minutes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                merchant_id,
                service['name'],
                service.get('price_at', 0),
                service.get('price_usd', 0),
                service.get('description', ''),
                service.get('duration_minutes', 60)
            ))
        
        handler.send_json({
            "message": "Merchant onboarded successfully",
            "merchant_id": merchant_id,
            "qr_url": f"/m/{merchant_id}"
        })
    
    @router.get('/m/<merchant_id>')
    def merchant_landing(handler, merchant_id):
        """Public merchant landing page (loaded by QR scan)"""
        merchant = ledger.query_one(
            "SELECT * FROM merchants WHERE merchant_id = ?",
            (merchant_id,)
        )
        
        if not merchant:
            return handler.send_error("Merchant not found", status=404)
        
        # Serve merchant landing HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{merchant['name']} | Ark OS</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="merchant-page">
                <h1>{merchant['name']}</h1>
                <p>{merchant['description']}</p>
                <div class="actions">
                    <a href="/kiosk.html?merchant={merchant_id}" class="btn">View Quests</a>
                    <a href="/wallet.html?pay={merchant_id}" class="btn">Pay with AT</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        handler.send_response(200)
        handler.send_header('Content-Type', 'text/html')
        handler.end_headers()
        handler.wfile.write(html.encode())
