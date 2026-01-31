import asyncio
import sys
import os

# FORZAR RUTA: Asegura que Python encuentre los módulos locales
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from database.db import engine, Base, AsyncSessionLocal
    from models.product import Product
    from sqlalchemy.ext.asyncio import AsyncSession
except ModuleNotFoundError as e:
    print(f"❌ Error: No se encontró el módulo. Verifica la estructura. Detalle: {e}")
    sys.exit(1)

async def init_models():
    print("⏳ Iniciando base de datos...")
    
    async with engine.begin() as conn:
        # Limpiamos las tablas anteriores para evitar duplicados en las pruebas
        print("🧹 Limpiando tablas existentes...")
        await conn.run_sync(Base.metadata.drop_all)
        print("🛠️ Creando nuevas tablas...")
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Lista de productos expandida para el inventario inteligente
            print("📦 Insertando catálogo de productos...")
            productos = [
                Product(name="Café Orgánico"),
                Product(name="Azúcar Morena"),
                Product(name="Leche de Almendras"),
                Product(name="Té Verde Antioxidante"),
                Product(name="Pan Artesanal"),
                Product(name="Miel de Abeja"),
                Product(name="Chocolate Amargo 70%"),
                Product(name="Avena en Hojuelas"),
                Product(name="Mermelada de Fresa"),
                Product(name="Aceite de Oliva")
            ]
            
            session.add_all(productos)
            
        await session.commit()
        
    print(f"✅ ¡Éxito! Se han creado las tablas e insertado {len(productos)} productos.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_models())