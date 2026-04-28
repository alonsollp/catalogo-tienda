import requests
import json
import os

TOKEN = os.getenv("LOYVERSE_TOKEN")
URL = "https://api.loyverse.com/v1.0/items"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def obtener_catalogo():
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Aquí tienes la lista de productos
        items = data.get('items', [])
        return items
    else:
        print(f"Error: {response.status_code}")
        return None
    
items = obtener_catalogo()

for p in items:
    nombre = p.get('item_name', 'Sin nombre')
    variantes = p.get('variants', [])
    
    if variantes:
        # Usamos 'default_price' que es lo que vimos en tu JSON
        precio = variantes[0].get('default_price', '0.00')
    else:
        precio = '0.00'
        
    print(f"Producto: {nombre:15} | Precio: S/. {precio}")




with open("index.html", "w", encoding="utf-8") as f:
    f.write("""
    <html>
    <head>
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>
        <style> .card-img-top { height: 250px; object-fit: cover; } </style>
    </head>
    <body class='bg-light'>
        <div class='container py-5'>
            <h1 class='text-center mb-5'>Catálogo de Productos</h1>
            <div class='row'>
    """)
    
    for p in items:
        nombre = p.get('item_name', 'Producto')
        variantes = p.get('variants', [])
        precio = variantes[0].get('default_price', '0.00') if variantes else '0.00'
        # Usamos la URL de la imagen que vimos en tu JSON
        imagen = p.get('image_url') or "https://via.placeholder.com/250"
        
        f.write(f"""
            <div class='col-md-4 mb-4'>
                <div class='card shadow-sm'>
                    <img src='{imagen}' class='card-img-top'>
                    <div class='card-body text-center'>
                        <h5 class='card-title'>{nombre}</h5>
                        <p class='text-primary fs-4'><strong>S/. {precio}</strong></p>
                    </div>
                </div>
            </div>
        """)
    
    f.write("</div></div></body></html>")

print("¡Listo! Abre 'catalogo_digital.html' en tu navegador.")