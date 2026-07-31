#!/usr/bin/env python3
"""
S3 Cleaner - Elimina TODOS los archivos del bucket automáticamente
"""

import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

BASE = "https://s3.todus.cu/stream"
NS = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def list_files(limit=10):
    """Lista archivos del bucket (10 en 10)"""
    try:
        url = f"{BASE}/?max-keys={limit}"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.text)
        files = []
        for item in root.findall('.//s3:Contents', NS):
            key = item.find('s3:Key', NS).text
            size = int(item.find('s3:Size', NS).text)
            files.append({'name': key, 'size': size})
        return files
    except Exception as e:
        log(f"Error: {e}")
        return []

def delete_files(files):
    """Elimina una lista de archivos"""
    deleted = 0
    errors = 0
    for f in files:
        try:
            r = requests.delete(f"{BASE}/{f['name']}", timeout=10)
            if r.status_code in [200, 204]:
                deleted += 1
                log(f"   ✅ {f['name']}")
            else:
                errors += 1
                log(f"   ⚠️ {f['name']} -> {r.status_code}")
        except Exception as e:
            errors += 1
            log(f"   ❌ {f['name']}")
        time.sleep(0.1)
    return deleted, errors

def clean_all():
    """Elimina TODOS los archivos del bucket (10 en 10)"""
    log("🧹 ELIMINANDO TODOS LOS ARCHIVOS DEL BUCKET...")
    log("=" * 50)
    
    total_deleted = 0
    total_errors = 0
    batch = 1
    
    while True:
        log(f"📦 Lote {batch} - Listando 10 archivos...")
        files = list_files(10)
        
        if not files:
            log("📭 No hay más archivos en el bucket")
            break
        
        total_size = sum(f['size'] for f in files)
        log(f"📋 {len(files)} archivos encontrados ({total_size/1024/1024:.2f} MB)")
        
        for f in files:
            log(f"   • {f['name']} ({f['size']/1024:.1f} KB)")
        
        log(f"🗑️ Eliminando {len(files)} archivos...")
        deleted, errors = delete_files(files)
        total_deleted += deleted
        total_errors += errors
        log(f"   ✅ Eliminados: {deleted}")
        log(f"   ❌ Errores: {errors}")
        
        batch += 1
        log("-" * 40)
    
    log("=" * 50)
    log(f"📊 RESUMEN FINAL:")
    log(f"   ✅ Total eliminados: {total_deleted}")
    log(f"   ❌ Total errores: {total_errors}")
    log("=" * 50)
    return total_deleted, total_errors

if __name__ == "__main__":
    log("🚀 INICIANDO S3 CLEANER...")
    log("⚠️  ¡ATENCIÓN! Se eliminarán TODOS los archivos del bucket")
    log("=" * 50)
    
    # Eliminar TODO automáticamente sin preguntar
    clean_all()
    
    log("✅ PROCESO COMPLETADO")