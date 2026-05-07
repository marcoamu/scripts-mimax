# NotebookLM Integration

## Estado Actual

✅ **CLI instalado:** `notebooklm` (v0.1.0)

### Lo que tenemos:
- Paquete npm instalado globalmente
- CLI con comandos disponibles
- Wrapper Python básico

### Lo que falta:
- 🔑 **Autenticación** - Necesita OAuth de Google
- 🌐 **Browser** - Playwright no funciona bien en headless

## Cómo autenticar (manual)

1. En tu máquina local (con navegador):
   ```bash
   notebooklm login
   ```
   Esto guarda las credenciales en `~/.notebooklm/storage-state.json`

2. Copia el archivo al servidor:
   ```bash
   scp ~/.notebooklm/storage-state.json usuario@servidor:~/.notebooklm/
   ```

3. Usa los comandos:
   ```bash
   notebooklm list
   notebooklm create "Mi Investigación"
   notebooklm generate audio <notebook_id>
   ```

## Alternativas

Si no podemos autenticar, podemos usar:

1. **Ollama + TTS** - Generar podcasts localmente
2. **Google Gemini API** - Para resúmenes de documentos
3. **YouTube Transcript + TTS** - Para podcasts de videos

## ¿Tienes credenciales de Google API?

Si tienes:
- Google Cloud OAuth credentials
- NotebookLM API key

我们可以 integrarlo directamente.
