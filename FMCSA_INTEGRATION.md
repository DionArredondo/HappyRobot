# FMCSA Integration Guide

## 🔐 Configuración Requerida

### 1. Obtener API Key de FMCSA

1. Dirígete a: https://data.transportation.gov/resource/yd7j-gg7b.api
2. Solicita una API Key gratuita (desarrollador)
3. Espera confirmación por email
4. Copia la API Key

### 2. Configurar en `.env`

```bash
# .env (ya parcialmente configurado)
FMCSA_API_KEY=your-fmcsa-api-key-here
```

**Reemplaza** `your-fmcsa-api-key-here` con tu API Key real.

## 📡 Endpoint Refactorizado

### POST `/validate-mc`

**URL**: `POST http://localhost:8000/validate-mc`

**Headers Requeridos**:
```
X-API-KEY: TU_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "carrier_mc": "123456"
}
```

**Response Exitosa (200)**:
```json
{
  "eligible": true,
  "operating_status": "ACTIVE",
  "safety_rating": "SATISFACTORY"
}
```

**Response - Transportista No Elegible**:
```json
{
  "eligible": false,
  "operating_status": "INACTIVE",
  "safety_rating": "UNSATISFACTORY"
}
```

**Response - API No Configurada (500)**:
```json
{
  "detail": "FMCSA API Key not configured. Please contact support."
}
```

## 🎯 Criterios de Elegibilidad (Reglas de Negocio)

| Criterio | Requerimiento | Resultado |
|----------|---------------|-----------|
| **allowedToOperate** | Debe ser `True` o `"Y"` | ✅ Pasa |
| **safetyRating** | NO debe ser `"UNSATISFACTORY"` | ✅ Pasa |
| **Ambas condiciones** | AMBAS deben cumplirse | ✅ `eligible=true` |

## 🛡️ Manejo de Errores

### Timeouts y Errores de Conexión (Fallback Seguro)

Si la API de FMCSA:
- No responde dentro de **5 segundos**
- Retorna error 5xx
- Tiene problemas de conexión

→ **Resultado**: `eligible=false`, `operating_status="INACTIVE"`

**Ventaja**: La llamada de voz **NO se cuelga** mientras espera respuesta de FMCSA.

### Errores Específicos

| Error | Código | Comportamiento |
|-------|--------|-----------------|
| MC no encontrado | 404 | `eligible=false` (fallback seguro) |
| API Key inválida | 403 | `eligible=false` (fallback seguro) |
| Timeout | N/A | `eligible=false` (fallback seguro) |
| API no configurada | 500 | Error HTTP 500 al cliente |

## 📊 Flujo de Ejecución

```
POST /validate-mc
    ↓
Validar FMCSA_API_KEY configurada
    ↓ (NO) → HTTPException 500
    ↓ (SÍ)
Llamar: GET https://api.fmcsa.dot.gov/v1/carriers/mc/{carrier_mc}?apiKey={key}
    ↓
¿Response válida (200)?
    ↓ (NO) → Fallback seguro: eligible=false
    ↓ (SÍ)
Parsear JSON y verificar:
  - allowedToOperate == True/Y?
  - safetyRating != "UNSATISFACTORY"?
    ↓
Retornar ValidateMCResponse con resultado
```

## 🧪 Testing Local

### 1. Con MC válido conocido (requiere FMCSA_API_KEY real):

```bash
curl -X POST http://localhost:8000/validate-mc \
  -H "X-API-KEY: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"carrier_mc": "123456"}'
```

### 2. Sin API Key configurada:

```bash
# Comentar FMCSA_API_KEY en .env
curl -X POST http://localhost:8000/validate-mc \
  -H "X-API-KEY: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"carrier_mc": "123456"}'

# Resultado esperado: HTTP 500 con mensaje de configuración
```

## 📝 Cambios Implementados

### ✅ `router/vetting.py`

1. **Funciones auxiliares**:
   - `_get_fmcsa_api_key()`: Valida que FMCSA_API_KEY esté configurada
   - `_fetch_carrier_data()`: Realiza llamada HTTP a FMCSA con timeout y error handling
   - `_evaluate_carrier_eligibility()`: Evalúa criterios de negocio

2. **Error Handling Robusto**:
   - Timeout: 5 segundos
   - Manejo de excepciones: `TimeoutException`, `RequestError`, `ValueError`
   - Fallback seguro: retorna `eligible=false` en caso de error

3. **Logging Completo**:
   - Errores de configuración
   - Fallos de conexión
   - Resultados finales de vetting

4. **Modelos Actualizados**:
   - `ValidateMCResponse` ahora incluye `safety_rating` real de FMCSA
   - Removido campo `active_insurance` (no proporcionado por FMCSA)

### ✅ `.env`

- Agregado placeholder `FMCSA_API_KEY=` con instrucciones

## 🚀 Próximos Pasos

1. **Obtener API Key real** en https://data.transportation.gov/resource/yd7j-gg7b.api
2. **Configurar `.env`** con tu API Key
3. **Testear endpoint** con MC numbers reales
4. **Validar logging** en logs de FastAPI
5. **Integrar en flujo de llamadas** de HappyRobot

## 📚 Referencias

- FMCSA Data API: https://data.transportation.gov/
- Documentación de MC Lookup: https://data.transportation.gov/resource/yd7j-gg7b.api
- httpx timeout docs: https://www.python-httpx.org/timeouts/

## ⚠️ Notas de Producción

- El timeout de 5 segundos es recomendado para no afectar la experiencia del usuario
- Considera agregar caché Redis para IDs de MC ya validados (opcional)
- Implementa rate limiting si el volumen es muy alto
- Monitorea errores de API en logs centralizados
