# 🚀 Deployment Guide - Branch: deploy_test

Esta rama contiene la versión refactorizada del proyecto con la nueva arquitectura multi-agente lista para testing y deployment.

## ⚠️ IMPORTANTE: Configuración de Seguridad

### 1. Variables de Ambiente
```bash
# NUNCA subas tu archivo .env al repositorio
cp .env.template .env
# Edita .env con tus claves reales
```

### 2. Configuración Rápida
```bash
# Clonar la rama específica
git clone -b deploy_test <tu-repositorio-url>
cd agente-groq-

# Configurar ambiente
cp .env.template .env
# Editar .env con tus API keys

# Instalar dependencias
pip install -r deployment/requirements.txt

# Ejecutar con Docker (RECOMENDADO)
docker-compose -f deployment/docker-compose.yml up --build
```

## 🐳 Deployment con Docker

### Desarrollo Local
```bash
docker-compose -f deployment/docker-compose.yml up --build
```

### Producción
```bash
# Crear .env.production con valores de producción
docker-compose -f deployment/docker-compose.yml -f deployment/docker-compose.prod.yml up -d
```

## 📊 Endpoints Disponibles

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8080/api/health
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuración por Cliente

Todos los ajustes específicos del cliente están en `/client_config/`:

- `branding.json` - Colores, logo, nombre de empresa
- `agents_config.json` - Definición de agentes y permisos
- `tools_schema.json` - Herramientas disponibles
- `entity_patterns.json` - Patrones de extracción de entidades
- `reference_map.json` - Mapeo de referencias contextuales

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest tests/

# Test de carga
locust -f tests/load_test.py --host=http://localhost:8080
```

## 📋 Checklist de Deployment

### Pre-Deployment
- [ ] Configurar variables de ambiente
- [ ] Verificar configuraciones en `client_config/`
- [ ] Ejecutar tests
- [ ] Verificar health checks

### Production Ready
- [ ] Configurar base de datos externa (PostgreSQL)
- [ ] Configurar gestión de secretos
- [ ] Implementar monitoreo (Prometheus/Grafana)
- [ ] Configurar alertas
- [ ] Configurar backup automático
- [ ] Implementar HTTPS
- [ ] Configurar rate limiting

## 🔍 Monitoring

### Health Checks
```bash
curl http://localhost:8080/api/health
curl http://localhost:8000/docs
```

### Logs
```bash
# Ver logs en tiempo real
docker-compose -f deployment/docker-compose.yml logs -f

# Logs específicos
tail -f logs/server.log
tail -f logs/agent_debug.log
```

## 🆘 Troubleshooting

### Problemas Comunes

1. **Error de API Key**
   ```bash
   # Verificar que .env existe y tiene las keys correctas
   cat .env | grep GROQ_API_KEY
   ```

2. **Puerto ocupado**
   ```bash
   # Cambiar puertos en docker-compose.yml o detener servicios
   docker-compose down
   ```

3. **Error de dependencias**
   ```bash
   # Reconstruir imagen
   docker-compose build --no-cache
   ```

## 📞 Soporte

Para problemas específicos de deployment:
1. Verificar logs en `/logs/`
2. Revisar configuración en `/client_config/`
3. Comprobar variables de ambiente
4. Verificar health endpoints

---

**Rama**: `deploy_test`  
**Fecha**: Julio 2025  
**Versión**: 2.0.0-beta
