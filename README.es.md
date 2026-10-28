# DSH Mobile

App Android para controlar **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** (DSH) desde el móvil.

> **No oficial.** Sin afiliación ni respaldo de DeepSeek. El nombre se usa para describir el software al que se conecta. DSH está en *developer preview* y puede romper compatibilidad.

<p align="center">
  <img src="docs/screenshots/pairing.png" width="260" alt="Pantalla de emparejamiento">
  <img src="docs/screenshots/dsh.png" width="260" alt="DSH dentro de la app">
</p>

## Qué es

Una carcasa **Capacitor** que abre la Web UI oficial de DSH en un WebView nativo, con lo que el móvil necesita:

- **Emparejamiento por QR** (URL + token) o URL manual.
- **Bloqueo biométrico** opcional antes de conectar.
- **Plugin nativo de navegación** para que la cookie `SameSite=Strict` de DSH se acepte.
- Icono y splash propios. Android 8+ (minSdk 26).

Los agentes, modelos y archivos siguen en tu ordenador: la app es un mando a distancia.

## Requisitos

| Dónde | Qué |
|---|---|
| Móvil | Android 8.0+ |
| Ordenador | Node.js 24.9+ y DSH con perfil web (`npx @deepseek-ai/dsh web`) |
| Red | **Tailscale recomendado** (móvil y PC en la misma tailnet, HTTPS con Tailscale Serve). También LAN o túnel TLS |

## Inicio rápido

1. **Arranca DSH en el PC**

   ```bash
   npx @deepseek-ai/dsh web --no-open --port 3080
   ```

2. **Expónlo al móvil** (Tailscale en ambos):

   ```bash
   tailscale serve --bg --https=443 http://127.0.0.1:3080
   npx @deepseek-ai/dsh web --no-open --port 3080 ^
     --trusted-host <maquina>.<tailnet>.ts.net ^
     --public-url https://<maquina>.<tailnet>.ts.net/
   ```

   En Windows cmd usa `^`; en macOS/Linux, barra invertida. Cualquier proxy HTTPS o IP de LAN también sirve (se permite HTTP en claro, pero HTTPS es más seguro).

3. **Helper opcional** del QR:

   ```bash
   npm install
   npm run pair
   ```

4. **Instala la app** desde [Releases](../../releases) (build debug para sideload) o compílala, **escanea el QR** y conecta.

## Compilar

Node.js 24.9+, JDK 21, Android SDK (platform 36, build-tools 36.x). Sin NDK.

```bash
npm install
npx cap sync android
cd android
./gradlew assembleDebug          # Windows: gradlew.bat assembleDebug
```

Wrapper con Gradle 9.0.0. App id: `io.github.deimerjr.dshmobile`.

## Cómo funciona

- Capacitor carga un shell local (`www/index.html`) para emparejar y pedir biometría.
- DSH emite su cookie con `SameSite=Strict`; navegar con `location.replace()` desde el shell es cross-site y Chrome descarta la cookie.
- Por eso navega un **plugin nativo** (`OpenUrlPlugin.java` → `WebView.loadUrl`), que envía cookies Strict como una navegación del navegador.
- El token se canjea por una cookie `HttpOnly`; la URL se guarda localmente. Si DSH se reinicia, vuelve a emparejar.

## Seguridad y privacidad

- El QR/URL contiene un **token de proceso**: no lo compartas.
- Token y URL se guardan en el almacenamiento privado de la app.
- **Sin analíticas, cuentas ni telemetría**: todo va a la URL que emparejas.
- Se permite HTTP en claro porque durante el setup se usan IPs de tailnet; prefiere HTTPS.
- La biometría es un bloqueo de conveniencia; la credencial real es la cookie.

## Limitaciones

- La Web UI de DSH está pensada para escritorio; en el móvil se ve ese layout.
- Sin notificaciones push.
- El botón atrás sale de la vista remota; reabre la app para volver al emparejamiento.
- Aún no hay build para iOS.
- DSH es developer preview: habrá cambios.

## Contribuir y licencia

Issues/PRs bienvenidos ([CONTRIBUTING.md](CONTRIBUTING.md)). MIT ([LICENSE](LICENSE)); terceros en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Read in English](README.md)
