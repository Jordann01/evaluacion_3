import pymongo
from datetime import datetime



cliente = pymongo.MongoClient("localhost", 27017)


db = cliente["mi_base"]


coleccion = db["salmones"]


documento = {
    "tipo": "Atlantico",
    "precio_venta": 5000,
    "precio_costo": 3000
}


coleccion.insert_one(documento)


for doc in coleccion.find():
    print(doc)

if coleccion.count_documents({}) == 0:
    coleccion.insert_many([
        {"tipo": "Atlantico", "venta": 5000, "costo": 3000, "stock": 100},
        {"tipo": "Nordico", "venta": 7000, "costo": 4500, "stock": 80},
        {"tipo": "Pacifico", "venta": 3000, "costo": 1500, "stock": 150}
    ])

# Mostrar todos los salmones
for doc in coleccion.find():
    print(doc)

usuarios = db["usuarios"]
pedidos = db["pedidos"]

# Insertar usuarios si no existen
if usuarios.count_documents({}) == 0:
    usuarios.insert_many([
        {"usuario": "admin", "contrasena": "1234", "rol": "admin"},
        {"usuario": "vendedor1", "contrasena": "1234", "rol": "vendedor"}
    ])

# Login
u = input("Usuario: ")
c = input("Contraseña: ")
user = usuarios.find_one({"usuario": u, "contrasena": c})

if not user:
    print("Login incorrecto.")
    exit()

print("Bienvenido")

# Menú
while True:
    if user["rol"] == "vendedor":
        print("1. Vender\n0. Salir")
        op = input("Opción: ")
        if op == "1":
            items = []
            for s in coleccion.find():
                print(s["tipo"])
            for _ in range(3):
                tipo = input("Tipo (enter para salir): ")
                if not tipo:
                    break
                kg = float(input("Kg: "))
                s = coleccion.find_one({"tipo": tipo})
                if not s or kg > s["stock"]:
                    print("Error.")
                    continue
                coleccion.update_one({"tipo": tipo}, {"$inc": {"stock": -kg}})
                items.append({"tipo": tipo, "kg": kg, "venta": s["venta"]})
            if items:
                pedidos.insert_one({"usuario": u, "fecha": datetime.now(), "items": items})
                print("Venta registrada.")
        else:
            break

    elif user["rol"] == "admin":
        print("1. Vender\n2. Ver pedidos\n3. Ver ganancias\n4. Editar stock\n0. Salir")
        op = input("Opción: ")
        if op == "1":
            items = []
            for s in coleccion.find():
                print(s["tipo"])
            for _ in range(3):
                tipo = input("Tipo (enter para salir): ")
                if not tipo:
                    break
                kg = float(input("Kg: "))
                s = coleccion.find_one({"tipo": tipo})
                if not s or kg > s["stock"]:
                    print("Error.")
                    continue
                coleccion.update_one({"tipo": tipo}, {"$inc": {"stock": -kg}})
                items.append({"tipo": tipo, "kg": kg, "venta": s["venta"]})
            if items:
                pedidos.insert_one({"usuario": u, "fecha": datetime.now(), "items": items})
                print("Venta registrada.")
        elif op == "2":
            for p in pedidos.find():
                print(p)
        elif op == "3":
            resumen = {}
            for p in pedidos.find():
                for i in p["items"]:
                    tipo = i["tipo"]
                    g = (i["venta"] - coleccion.find_one({"tipo": tipo})["costo"]) * i["kg"]
                    resumen[tipo] = resumen.get(tipo, 0) + g
            for t in resumen:
                print(t, resumen[t])
        elif op == "4":
            for s in coleccion.find():
                print(s["tipo"], s["stock"])
            tipo = input("Tipo: ")
            nuevo = float(input("Nuevo stock: "))
            coleccion.update_one({"tipo": tipo}, {"$set": {"stock": nuevo}})
            print("Stock actualizado.")
        else:
            break
    
