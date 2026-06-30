# 🚀 FMCSA Integration - Quick Start (5 minutos)

## ⚡ Pasos Rápidos

### Paso 1: Obtener API Key (3 minutos)

```
1. Ve a: https://data.transportation.gov/resource/yd7j-gg7b.api
2. Haz clic en "API Docs" o "Sign Up"
3. Crea cuenta desarrollador (gratis, solo email)
4. Genera API Key
5. Copia la clave
```

### Paso 2: Configurar `.env` (30 segundos)

```bash
# Archivo: .env (en la raíz del proyecto)

# Reemplaza esto:
FMCSA_API_KEY=

# Por esto (pega tu clave):
FMCSA_API_KEY=your-actual-key-from-step-1
```

### Paso 3: Verificar Dependencias (1 minuto)

```bash
cd backend
pip install -r requirements.txt
```

(Verifica que `httpx` está en la salida)

### Paso 4: Probar Integración (1 minuto)

**Terminal 1:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2:**
```bash
cd backend
python test_vetting.py
```

**Esperado:**
```
Test 1: Valid MC (should call FMCSA if key configured)
Status Code: 200
Response:
{
  "eligible": true,
  "operating_status": "ACTIVE",
  "safety_rating": "SATISFACTORY"
}
✅ Response structure is correct
```

---

## 📋 Checklist de Implementación

- [ ] API Key obtenida
- [ ] `.env` configurado
- [ ] `pip install -r requirements.txt` ejecutado
- [ ] `test_vetting.py` ejecutado exitosamente
- [ ] `safety_rating` aparece en la respuesta
- [ ] Sin errores HTTP 500
- [ ] Logs muestran intentos de FMCSA

---

## 🔍 Verificación

### Ver que esté funcionando:

```bash
# Opción 1: Usar curl
curl -X POST http://localhost:8000/validate-mc \
  -H "X-API-KEY: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"carrier_mc": "123456"}'

# Opción 2: Ver logs en FastAPI
# Deberías ver en la consola:
# INFO - MC 123456 vetting result: eligible=...
```

### Respuesta Esperada:

```json
{
  "eligible": true,
  "operating_status": "ACTIVE",
  "safety_rating": "SATISFACTORY"
}
```

---

## ⚠️ Solución de Problemas Rápida

### Error 500 "API Key not configured"
```bash
# Verificar .env existe:
cat .env | grep FMCSA_API_KEY

# Si está vacío:
# FMCSA_API_KEY=
# Asegúrate de pegar tu clave y reinicia uvicorn
```

### Timeout o No hay respuesta
```bash
# 1. Verifica internet:
ping api.fmcsa.dot.gov

# 2. Prueba API Key:
curl "https://api.fmcsa.dot.gov/v1/carriers/mc/123456?apiKey=YOUR_KEY"

# 3. Si falla, la clave es inválida o expiró
```

### ImportError: httpx
```bash
pip install httpx
# Ya debería estar en requirements.txt
```

---

## 📞 Contactos Útiles

| Recurso | Link |
|---------|------|
| FMCSA API Portal | https://data.transportation.gov/ |
| Documentación API | https://data.transportation.gov/resource/yd7j-gg7b.api |
| Generar API Key | https://data.transportation.gov/resource/yd7j-gg7b.api |

---

## 📚 Documentación Completa

Para más detalles, consulta:
- `FMCSA_INTEGRATION.md` - Guía completa de configuración
- `CHANGES_SUMMARY.md` - Cambios técnicos detallados
- `ARCHITECTURE_FMCSA.md` - Diagramas de arquitectura

---

## ✨ Resumen de lo que se implementó

✅ Llamadas HTTP reales a FMCSA  
✅ Validación de API Key desde `.env`  
✅ Timeout de 5 segundos (no bloquea llamadas de voz)  
✅ Fallback seguro en caso de errores  
✅ Logging completo para debugging  
✅ Manejo robusto de excepciones  
✅ Criterios de elegibilidad FMCSA (authorized + safety rating)  
✅ Script de pruebas incluido  

---

**¡Listo para usar!** 🎉 Sigue los 4 pasos y estarás corriendo en ~5 minutos.
