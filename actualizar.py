import requests
import json
import os
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("LOYVERSE_TOKEN")
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
            # Usamos 'inventory_levels' que es el campo real de la API
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
        <title>Nuestro Catálogo Digital</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
        <style>
            :root {{ --primary-color: #25D366; --dark-color: #121b22; }}
            body {{ background-color: #f8f9fa; font-family: 'Segoe UI', system-ui, sans-serif; }}
            .navbar {{ background-color: var(--dark-color); color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
            
            .card {{ 
                border: none; 
                border-radius: 18px; 
                overflow: hidden; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
                height: 100%; 
                display: flex; 
                flex-direction: column; 
                transition: transform 0.2s; 
                background: white;
            }}
            .card:active {{ transform: scale(0.97); }}

            /* Contenedor de imagen uniforme */
            .img-container {{
                height: 160px;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #fdfdfd;
                overflow: hidden;
            }}

            .card-img-top {{ 
                max-height: 100%;
                max-width: 100%;
                object-fit: contain; 
                padding: 10px; 
            }}

            .no-image-icon {{
                font-size: 3.5rem;
                color: #dee2e6;
            }}

            .card-body {{ 
                padding: 15px; 
                display: flex; 
                flex-direction: column; 
                flex-grow: 1; 
                text-align: center;
            }}

            .card-title {{ 
                font-size: 0.95rem; 
                font-weight: 600; 
                text-transform: capitalize; 
                color: #333;
                margin-bottom: 10px;
                height: 2.5em;
                overflow: hidden;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }}

            .price-tag {{ 
                font-size: 1.25rem; 
                font-weight: 800; 
                color: #111;
                margin-top: auto; 
                margin-bottom: 15px; 
            }}

            .btn-whatsapp {{ 
                background-color: var(--primary-color); 
                color: white; 
                border-radius: 12px; 
                font-weight: 700; 
                text-decoration: none; 
                padding: 10px; 
                border: none;
                transition: 0.2s;
            }}
            .btn-whatsapp:hover {{ background-color: #1ebc5a; color: white; }}

            .badge-stock {{ 
                position: absolute; 
                top: 12px; 
                right: 12px; 
                font-size: 0.7rem; 
                padding: 5px 12px; 
                border-radius: 50px; 
                font-weight: 600;
                z-index: 10;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar sticky-top py-3 mb-4">
            <div class="container d-flex justify-content-center">
                <h5 class="mb-0 fw-bold">🛒 Nuestro Catálogo</h5>
            </div>
        </nav>

        <div class="container pb-5">
            <div class="row gx-3 gy-4">
    """)

    for p in items:
        nombre = p.get('item_name', 'Producto')
        variantes = p.get('variants', [])
        v = variantes[0] if variantes else {}
        v_id = v.get('variant_id')
        precio = v.get('default_price', '0.00')
        
        # --- LÓGICA DE IMAGEN O ICONO ---
        image_url = p.get('image_url')
        if image_url:
            display_media = f'<img src="{image_url}" class="card-img-top" loading="lazy">'
        else:
            # Icono de caja calada cuando no hay foto
            display_media = '<i class="bi bi-box-seam no-image-icon"></i>'
        
        # --- LÓGICA DE STOCK ---
        stock_actual = dict_stock.get(v_id)

        if stock_actual is not None and float(stock_actual) <= 0:
            badge = '<span class="badge bg-danger badge-stock">Agotado</span>'
            btn_style = "opacity: 0.5; pointer-events: none; background-color: #6c757d;"
            texto_boton = "Sin Stock"
        else:
            info = f"Stock: {int(stock_actual)}" if stock_actual is not None else "Disponible"
            badge = f'<span class="badge bg-success badge-stock">{info}</span>'
            btn_style = ""
            texto_boton = '<i class="bi bi-whatsapp me-2"></i>Pedir'

        msg = urllib.parse.quote(f"¡Hola! Me interesa este producto: {nombre} (S/ {precio})")
        link_wa = f"https://wa.me/{TELEFONO_TIENDA}?text={msg}"

        f.write(f"""
                <div class="col-6 col-md-4 col-lg-3">
                    <div class="card position-relative">
                        {badge}
                        <div class="img-container">
                            {display_media}
                        </div>
                        <div class="card-body">
                            <div class="card-title">{nombre}</div>
                            <div class="price-tag">S/ {precio}</div>
                            <a href="{link_wa}" target="_blank" class="btn btn-whatsapp" style="{btn_style}">
                                {texto_boton}
                            </a>
                        </div>
                    </div>
                </div>
        """)

    f.write(f"""
            </div>
        </div>
        <div class="text-center pb-5 text-muted small">
            <p>Gracias por comprar con nosotros ✨</p>
            <p style="font-size: 0.7rem;">Sincronizado: {fecha_act}</p>
        </div>
    </body>
    </html>
    """)

print(f"Éxito: Catálogo generado con {len(items)} productos.")