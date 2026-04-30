import requests
import json
import os
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "d3afc1d40fbc4265a0e6a54ebd2cdca7"
#os.getenv("LOYVERSE_TOKEN")
URL_ITEMS = "https://api.loyverse.com/v1.0/items"
URL_INVENTARIO = "https://api.loyverse.com/v1.0/inventory"
TELEFONO_TIENDA = "51997475790" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def obtener_stock_real():
    try:
        res = requests.get(URL_INVENTARIO, headers=headers)
        if res.status_code == 200:
            data = res.json()
            niveles = data.get('inventory_levels', [])
            return {inv['variant_id']: inv['in_stock'] for inv in niveles}
    except Exception as e:
        print(f"Error inventario: {e}")
    return {}

def obtener_catalogo():
    try:
        res = requests.get(URL_ITEMS, headers=headers)
        if res.status_code == 200:
            return res.json().get('items', [])
    except Exception as e:
        print(f"Error catálogo: {e}")
    return []

# --- PROCESAMIENTO ---
dict_stock = obtener_stock_real()
items = obtener_catalogo()
fecha_act = datetime.now().strftime("%d/%m/%Y %I:%M %p")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo con Pedido Único</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            :root {{ --primary-color: #25D366; --dark-color: #121b22; }}
            body {{ background-color: #f4f7f6; font-family: 'Segoe UI', system-ui, sans-serif; }}
            .navbar {{ background-color: var(--dark-color); color: white; }}
            
            .card {{ 
                border: none; border-radius: 15px; overflow: hidden; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.05); height: 100%; 
                background: white; transition: 0.2s;
            }}
            .card.selected {{ border: 2px solid var(--primary-color); background: #e8f9ef; }}

            .img-container {{
                height: 140px; display: flex; align-items: center;
                justify-content: center; background: #fff;
            }}
            .card-img-top {{ max-height: 100%; max-width: 100%; object-fit: contain; padding: 10px; }}
            .no-image-icon {{ font-size: 3rem; color: #dee2e6; }}

            /* Botón de selección */
            .btn-check-item {{
                width: 100%; border-radius: 10px; font-weight: 700;
                transition: 0.3s; border: 2px solid var(--primary-color);
                color: var(--primary-color); background: transparent;
            }}
            .btn-check-item.active {{
                background-color: var(--primary-color); color: white;
            }}

            /* Carrito Flotante */
            #cart-floating {{
                position: fixed; bottom: 20px; right: 20px; z-index: 1000;
                background: var(--primary-color); color: white; border: none;
                border-radius: 50px; padding: 15px 25px; font-weight: 800;
                box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4);
                display: none; align-items: center; gap: 10px;
                transition: transform 0.3s ease;
            }}
            #cart-floating:hover {{ transform: scale(1.05); }}
            
            .price-tag {{ font-size: 1.1rem; font-weight: 800; color: #111; }}
            .badge-stock {{ position: absolute; top: 10px; right: 10px; font-size: 0.65rem; }}
        </style>
    </head>
    <body>
        <nav class="navbar sticky-top py-3 mb-4 text-center">
            <div class="container d-flex justify-content-center">
                <h5 class="mb-0 fw-bold"><i class="bi bi-shop me-2"></i>Catálogo de la Tienda</h5>
            </div>
        </nav>

        <div class="container pb-5">
            <div class="row gx-2 gy-3">
    """)

    for p in items:
        nombre = p.get('item_name', 'Producto').replace('"', "'")
        variantes = p.get('variants', [])
        v = variantes[0] if variantes else {}
        v_id = v.get('variant_id')
        precio = v.get('default_price', '0.00')
        img_url = p.get('image_url')
        stock_actual = dict_stock.get(v_id)

        # Lógica de imagen
        media = f'<img src="{img_url}" class="card-img-top" loading="lazy">' if img_url else '<i class="bi bi-box-seam no-image-icon"></i>'
        
        # Lógica de stock
        is_out = stock_actual is not None and float(stock_actual) <= 0
        stock_label = "Agotado" if is_out else (f"Stock: {int(stock_actual)}" if stock_actual is not None else "Disponible")
        badge_class = "bg-danger" if is_out else "bg-success"

        f.write(f"""
                <div class="col-6 col-md-4 col-lg-2">
                    <div class="card position-relative" id="card-{v_id}">
                        <span class="badge {badge_class} badge-stock">{stock_label}</span>
                        <div class="img-container">{media}</div>
                        <div class="card-body p-2">
                            <div class="card-title mb-1 small fw-bold">{nombre}</div>
                            <div class="price-tag mb-2">S/ {precio}</div>
                            
                            <button class="btn btn-check-item btn-sm" 
                                    onclick="toggleItem('{v_id}', '{nombre}', '{precio}')"
                                    {"disabled" if is_out else ""}>
                                { "Agotado" if is_out else "Seleccionar" }
                            </button>
                        </div>
                    </div>
                </div>
        """)

    f.write(f"""
            </div>
        </div>

        <!-- Botón Flotante de WhatsApp -->
        <button id="cart-floating" onclick="sendOrder()">
            <i class="bi bi-whatsapp fs-4"></i>
            <span>Enviar Pedido (<span id="cart-count">0</span>)</span>
        </button>

        <script>
            let cart = [];
            const whatsappNumber = "{TELEFONO_TIENDA}";

            function toggleItem(id, name, price) {{
                const index = cart.findIndex(item => item.id === id);
                const card = document.getElementById('card-' + id);
                const btn = card.querySelector('.btn-check-item');

                if (index > -1) {{
                    cart.splice(index, 1);
                    card.classList.remove('selected');
                    btn.classList.remove('active');
                    btn.innerText = 'Seleccionar';
                }} else {{
                    cart.push({{ id, name, price }});
                    card.classList.add('selected');
                    btn.classList.add('active');
                    btn.innerText = '✓ Añadido';
                }}
                updateCartUI();
            }}

            function updateCartUI() {{
                const btnFloating = document.getElementById('cart-floating');
                const countSpan = document.getElementById('cart-count');
                countSpan.innerText = cart.length;
                btnFloating.style.display = cart.length > 0 ? 'flex' : 'none';
            }}

            function sendOrder() {{
                let message = "¡Hola! Quisiera realizar un pedido:\\n\\n";
                let total = 0;
                
                cart.forEach((item, i) => {{
                    message += (i+1) + ". " + item.name + " - S/ " + item.price + "\\n";
                    total += parseFloat(item.price);
                }});

                message += "\\n*Total estimado: S/ " + total.toFixed(2) + "*";
                const encodedMsg = encodeURIComponent(message);
                window.open("https://wa.me/" + whatsappNumber + "?text=" + encodedMsg, '_blank');
            }}
        </script>

        <div class="text-center pb-5 text-muted small">
            <p style="font-size: 0.7rem;">Sincronizado: {fecha_act}</p>
        </div>
    </body>
    </html>
    """)