# DSH Mobile

Cliente Android **no oficial** para **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** (DSH): abre la Web UI oficial dentro de un WebView nativo y añade emparejamiento por QR y bloqueo biométrico opcional.

> **No afiliado a DeepSeek.** El nombre se usa para describir el software al que se conecta. DSH está en *developer preview* y cambia a menudo. El APK de Releases es un **build debug** para uso personal/sideload, no una app de Play Store.

<p align="center">
  <img src="docs/screenshots/pairing.png" width="260" alt="Pantalla de emparejamiento">
  <img src="docs/screenshots/dsh.png" width="260" alt="DSH dentro de la app">
</p>

## Índice

1. [Qué es y qué no es](#qué-es-y-qué-no-es)
2. [Cómo funciona](#cómo-funciona)
3. [Requisitos](#requisitos)
4. [Instalar la app](#instalar-la-app)
5. [Preparar DSH en el ordenador](#preparar-dsh-en-el-ordenador)
6. [Exponer DSH al móvil](#exponer-dsh-al-móvil)
7. [Emparejar](#emparejar)
8. [Verificar](#verificar)
9. [Problemas frecuentes](#problemas-frecuentes)
10. [Seguridad y privacidad](#seguridad-y-privacidad)
11. [Limitaciones](#limitaciones)
12. [Preguntas frecuentes](#preguntas-frecuentes)
13. [Compilar desde el código](#compilar-desde-el-código)
14. [Estructura del proyecto](#estructura-del-proyecto)

---

## Qué es y qué no es

**Es** una carcasa fina: la Web UI real la sirve **tu ordenador** y la app la pinta en un WebView de Android. La app solo guarda la URL, empareja con QR y (opcionalmente) pide huella antes de conectar.

**No es** una reimplementación móvil de DSH, y **no incluye Tailscale**. Dentro del APK no hay servidor DSH, ni clave de API de modelos, ni VPN.

---

## Cómo funciona

```text
Móvil                                      Ordenador
+---------------------------+              +--------------------------------------+
|  DSH Mobile (WebView)     |   HTTPS      |  Tailscale (WireGuard)               |
|      |                    |   por        |      |                               |
|      +--> URL de tailnet  |   tailnet    |      +--> tailscale serve :443        |
|                           |              |                |                     |
+---------------------------+              |                +--> 127.0.0.1:3080   |
                                           |                        DSH web      |
                                           +--------------------------------------+
```

Puntos clave:

- La app necesita una URL alcanzable desde el móvil. **Tailscale es lo recomendado**, pero la app es agnóstica: también sirven LAN o cualquier túnel HTTPS.
- Tailscale debe estar instalado y activo en **los dos** dispositivos, y `tailscale serve` (u otro proxy HTTPS) expone el DSH que escucha en loopback.
- La cookie de sesión de DSH usa `SameSite=Strict`. Por eso la app navega mediante un **plugin nativo** (`WebView.loadUrl`) en vez de JavaScript. Si haces fork, no lo cambies por `location.replace()`: el canje del token fallaría.

---

## Requisitos

### Móvil

| Requisito | Notas |
|---|---|
| Android 8.0+ (API 26) | Target SDK 36 |
| Cámara | Solo para escanear el QR; también puedes pegar la URL |
| App Tailscale (recomendada) | Inicia sesión con la **misma cuenta** que el PC. Solo necesaria si usas Tailscale |

### Ordenador (donde corre DSH)

| Requisito | Notas |
|---|---|
| Node.js **24.9+** | Es el mínimo que exige DSH |
| DSH desde npm | `npx @deepseek-ai/dsh web` lo descarga y ejecuta |
| DSH configurado | Modelo/clave de API listos; si no, la UI carga pero no responde |
| Exposición de red | Tailscale Serve, bind a LAN o túnel TLS (ver abajo) |
| Opcional: Tailscale | Instalado y logueado en la misma tailnet que el móvil |
| Opcional: Tailscale Serve | **Desactivado por defecto.** Debe habilitarse para la tailnet en el panel de administración de Tailscale |

### Para compilar el APK (solo si no usas Releases)

| Requisito | Notas |
|---|---|
| Node.js 24.9+ | Capacitor y scripts npm |
| JDK 21 | Gradle se ejecuta sobre él |
| Android SDK | Platform 36 + build-tools 36.x |
| Gradle | Lo trae el wrapper (9.0.0) |
| NDK | **No hace falta** |

---

## Instalar la app

### Opción A: APK de Releases (lo más rápido)

1. Abre **[Releases](https://github.com/deimerjr/dsh-mobile/releases)** y descarga `dsh-mobile-0.1.0-debug.apk`.
2. En el móvil, permite instalar apps desconocidas para el explorador que uses y abre el APK.
3. Si tenías otra build con distinto app id, desinstálala antes: son paquetes distintos.

### Opción B: compilar

Ver [Compilar desde el código](#compilar-desde-el-código).

---

## Preparar DSH en el ordenador

1. Instala **Node.js 24.9 o superior** (`node --version`).
2. Arranca la Web UI en loopback:

   ```bash
   npx @deepseek-ai/dsh web --no-open --port 3080
   ```

   La primera vez descarga DSH. Espera a que imprima `dsh web: http://127.0.0.1:3080/?token=...`.
   **Deja esa terminal abierta**: es el servidor.

3. Abre esa URL en el navegador del propio PC y confirma que DSH funciona (modelo configurado, workspace elegido).

> DSH guarda sesiones y credenciales en `~/.dsh`. Se comparten con otros perfiles de DSH de la misma máquina.

---

## Exponer DSH al móvil

Elige **una** opción. Tailscale es lo recomendado: cifra el tráfico y no expone DSH a Internet.

### Opción 1: Tailscale + Tailscale Serve (recomendada)

Una sola vez:

1. Instala **Tailscale** en el ordenador y en el móvil e inicia sesión con la **misma cuenta**.
2. En el panel de administración de Tailscale, habilita **Serve** para la tailnet (viene desactivado). El propio comando te da el enlace de activación si está apagado.
3. Obtén el nombre de tu máquina en la tailnet:

   ```bash
   # macOS / Linux
   tailscale status --json | jq -r .Self.DNSName

   # Windows PowerShell
   (tailscale status --json | ConvertFrom-Json).Self.DNSName
   ```

   Se parece a `mi-pc.tailXXXX.ts.net` (sin el punto final).

4. Publica el DSH local por HTTPS:

   ```bash
   tailscale serve --bg --https=443 http://127.0.0.1:3080
   tailscale serve status     # debe mostrar https://<tu-host> -> http://127.0.0.1:3080
   ```

5. Reinicia DSH para que acepte el host público y anuncie la URL HTTPS:

   ```bash
   npx @deepseek-ai/dsh web --no-open --port 3080 ^
     --trusted-host <tu-host> ^
     --public-url https://<tu-host>/
   ```

   (En macOS/Linux usa barra invertida en vez de `^`.) Ahora DSH imprime `dsh web: https://<tu-host>/?token=...`.

> ¿Por qué `--trusted-host`? DSH comprueba la cabecera HTTP `Host`. A través de Serve la cabecera es el nombre de tailnet, así que DSH debe aceptarlo. `--public-url` solo cambia lo que DSH imprime y anuncia.
>
> Nota: en Windows normalmente **no** podrás abrir `https://<tu-host>/` desde el mismo PC. Prueba desde el móvil.

### Opción 2: LAN (misma Wi-Fi)

```bash
npx @deepseek-ai/dsh web --no-open --port 3080 --host 192.168.1.50
```

Usa la IPv4 de tu PC en la LAN. Permite TCP 3080 en el firewall y abre `http://192.168.1.50:3080/?token=...` en el móvil. Es tráfico sin cifrar y solo funciona en la misma red.

### Opción 3: túnel HTTPS

Cualquier túnel que apunte a `http://127.0.0.1:3080`, por ejemplo:

```bash
cloudflared tunnel --url http://127.0.0.1:3080
```

Luego reinicia DSH con `--trusted-host <host-del-tunel> --public-url https://<host-del-tunel>/`. Protege el túnel con el control de acceso del proveedor: el token de la URL es una credencial.

---

## Emparejar

### Helper (imprime un QR en la terminal)

El helper arranca DSH con los flags que le pases e imprime un QR:

```bash
npm install
npm run pair -- --host 127.0.0.1 --port 3080 ^
  --trusted-host <tu-host> --public-url https://<tu-host>/
```

(Windows `^`, macOS/Linux barra invertida.) **No** configura Tailscale Serve: hazlo antes (sección anterior).

### Manual

1. Copia la URL `dsh web: https://.../?token=...` que imprime DSH.
2. Abre DSH Mobile, pégala en **Emparejar** y pulsa **Guardar y conectar**.
3. O genera un QR con cualquier herramienta y escanéalo.

### Qué se guarda

La app guarda la URL **con el token** en el almacenamiento privado para poder reconectar. El token se canjea por una cookie `HttpOnly` al cargar. Cuando DSH se reinicia el token rota: abre la app y pulsa **Olvidar**, luego escanea el QR nuevo.

---

## Verificar

1. En el móvil, con Tailscale activo, abre la URL **primero en Chrome**. Debes ver la UI de DSH. Si Chrome no puede, la app tampoco.
2. Abre DSH Mobile y pulsa **Conectar**; aprueba la biometría si la pide.
3. Debes ver el chat de DSH. Elige un workspace y envía un mensaje de prueba.

---

## Problemas frecuentes

| Síntoma | Causa / solución |
|---|---|
| `dsh web authentication required` | Token caducado o DSH reiniciado. App: **Olvidar** y escanea el QR nuevo. |
| Chrome no abre `https://<host>/` | Tailscale apagado en el móvil, Serve sin configurar, host incorrecto o DSH no escuchando en 127.0.0.1. Revisa `tailscale serve status` y `tailscale ping <movil>`. |
| `ERR_CONNECTION_REFUSED` o timeout en LAN | Firewall bloqueando 3080, IP incorrecta o DSH en 127.0.0.1 en vez de la IP de LAN. |
| `403` / forbidden | `--trusted-host` no coincide con el host de la URL (tailnet vs. nombre del túnel). |
| Se queda en el splash | El primer arranque del WebView es lento; espera y reabre. |
| Biometría cancelada | Pulsa **Conectar** otra vez; **Probar** prueba el diálogo sin conectar. Los fallos técnicos se omiten; solo cancela el usuario. |
| El QR no escanea | Falta permiso de cámara o no hay cámara. Pega la URL a mano. |
| `tailscale serve` dice que no está habilitado | Activa Serve para la tailnet en el panel (el comando imprime el enlace) y reintenta. |

---

## Seguridad y privacidad

- La URL/QR contiene un **token de proceso**. Trátalo como una contraseña y no publiques capturas que lo muestren.
- El token y la URL viven en el almacenamiento privado de la app. **Sin analíticas, cuentas, telemetría ni servidores de terceros**: el tráfico va solo a la URL que emparejas.
- Se permite HTTP en claro porque durante el setup se usan IPs de LAN/tailnet. Prefiere HTTPS.
- La biometría es un bloqueo de comodidad, no una frontera de seguridad: la credencial real es la cookie de DSH.
- Quien alcance tu URL y tu token puede controlar tus agentes. Mantén las ACL de Tailscale estrictas y no expongas DSH públicamente sin control de acceso.

---

## Limitaciones

- La Web UI de DSH está pensada para escritorio; en el móvil se ve un layout de escritorio.
- Sin notificaciones push.
- El botón atrás sale de la vista remota; reabre la app para volver al emparejamiento.
- Sin build para iOS.
- Un solo servidor a la vez, sin selector multi-PC.
- El APK de Releases está **firmado en debug**; no puede actualizar sobre una build firmada de release.
- DSH es developer preview: los cambios pueden requerir actualizar la app.

---

## Preguntas frecuentes

**¿La app integra Tailscale?** No. Usa la app de Tailscale del móvil y del PC. El APK no lleva VPN, ni SDK de Tailscale, ni login de cuenta.

**¿Se puede usar sin Tailscale?** Sí: bind a LAN o un túnel HTTPS.

**¿DSH corre en el móvil?** No. Corre en el PC; el móvil es un mando a distancia.

**¿Puedo conectar varias PCs?** Todavía no; se guarda un servidor a la vez.

**¿Está en Google Play?** No. La build actual es un APK debug para sideload.

**¿Por qué no responde a mi primer mensaje?** Comprueba que DSH funciona en el PC (modelo/clave configurados) y que hay un workspace seleccionado.

---

## Compilar desde el código

Requisitos: Node.js 24.9+, JDK 21, Android SDK platform 36 y build-tools 36.x (con `ANDROID_HOME`). Sin NDK.

```bash
git clone https://github.com/deimerjr/dsh-mobile.git
cd dsh-mobile
npm install
npx cap sync android
cd android
./gradlew assembleDebug        # Windows: gradlew.bat assembleDebug
```

APK: `android/app/build/outputs/apk/debug/app-debug.apk`.

El app id es `io.github.deimerjr.dshmobile`. Si haces fork y publicas, cámbialo en `capacitor.config.json`, `android/app/build.gradle`, `strings.xml` y el paquete Java, o las instalaciones chocarán.

---

## Estructura del proyecto

```text
www/index.html                 shell de emparejamiento (HTML/CSS/JS, sin bundler)
capacitor.config.json          app id, web dir, allowlist de navegación
tools/pair.mjs                 helper de emparejamiento con QR (Node)
tools/make-icons.py            generador de iconos y splash
android/                       proyecto Android de Capacitor
  app/src/main/java/io/github/deimerjr/dshmobile/
    MainActivity.java          registra OpenUrlPlugin
    OpenUrlPlugin.java         navegación nativa (fix SameSite)
docs/screenshots/              capturas usadas en este README
```

## Contribuir y licencia

Issues y PRs bienvenidos; ver [CONTRIBUTING.md](CONTRIBUTING.md). Licencia MIT ([LICENSE](LICENSE)); terceros en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Read in English](README.md)
