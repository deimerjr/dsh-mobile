# DSH Mobile — qué falta para que lo use cualquier usuario

Estado actual: APK **debug**, emparejado a **tu** PC por Tailscale, con un QR generado por un
script de PowerShell en Windows. Funciona para ti; para terceros hay que separar tres cosas:
**producto genérico**, **distribución** y **onboarding/soporte**.

---

## 1. Decisiones de producto (antes de tocar código)

| Pregunta | Opciones | Recomendación |
|---|---|---|
| ¿Cada usuario corre su propio DSH? | (a) sí, en su PC/servidor; (b) DSH alojado por ti | (a) para MVP: menos infra, menos responsabilidad |
| ¿Cómo llega el móvil al DSH? | Tailscale por usuario, LAN, Cloudflare Tunnel, relay propio | Tailscale (BYO) documentado; relay propio solo si quieres masivo |
| ¿Android, iOS o ambos? | Android ya; iOS requiere Mac + Apple Developer (99 EUR/año) | Android primero |
| ¿Gratis o de pago? | Play gratis / pago / open source | Open source + APK firmado reduce fricción legal |

> DSH está en **developer preview** y rompe compatibilidad. Si distribuyes masivamente, tendrás que
> fijar y probar versiones de DSH.

---

## 2. Cambios técnicos en la app (obligatorios)

- [ ] **Quitar la allowlist fija de hosts.** La allowlist ya esta abierta (`server.allowNavigation: ["*"]`) para aceptar cualquier host emparejado;
      para produccion conviene una regla nativa limitada al host del QR.
- [ ] **Helper de emparejamiento multiplataforma.** Hoy el QR lo genera `start-mobile.ps1` (solo Windows).
      Alternativa: pequeño CLI Node (`npx dsh-mobile-pair`) o plugin de DSH que imprima el QR en terminal.
- [ ] **Deep link** `dsmobile://pair?url=...` para que el QR abra la app directamente (y no Chrome).
- [ ] **Validación y errores de red**: distinguir DNS, TLS, 401/403, timeout, Tailscale apagado; botón reintentar.
- [ ] **Modo sin biometría** explícito (hoy la biometría puede bloquear si el plugin falla).
- [ ] **Multi-servidor** (lista de PCs) y renombrar destinos.
- [ ] **i18n**: mínimo español + inglés; Play agradece descripción en inglés.
- [ ] **Compatibilidad DSH**: detectar versión/URL inválida y avisar.
- [ ] **Reconexión**: si DSH se reinicia, el token caduca; guiar a re-emparejar sin perder la app.
- [ ] **UX móvil**: a ~410 CSS px la Web UI de DSH usa el layout de escritorio. Decidir si se acepta
      o se inyecta CSS/zoom para forzar el modo móvil.

---

## 3. Firma y build de release (obligatorio)

- [ ] Generar keystore propio:
      `keytool -genkeypair -v -keystore dsh-mobile.keystore -alias dsh -keyalg RSA -keysize 2048 -validity 10000`
- [ ] Configurar `signingConfig` en `android/app/build.gradle` (sin subir el keystore al repo).
- [ ] `assembleRelease` → APK firmado, o `bundleRelease` → **AAB** (obligatorio para Play).
- [ ] Guardar keystore + contraseñas en un gestor; **perderlo = no poder actualizar la app** (salvo Play App Signing).
- [ ] Versionado: `versionCode` incremental y `versionName` semántico.

---

## 4. Google Play (si quieres distribución masiva)

- [ ] Cuenta de desarrollador: **25 USD único** + verificación de identidad.
- [ ] **AAB** firmado, `targetSdk` reciente (la app ya usa 36), minSdk 26.
- [ ] Play App Signing activado (Google guarda la clave de distribución).
- [ ] Ficha: nombre, descripción corta/larga, icono 512x512, *feature graphic* 1024x500, al menos
      2-8 capturas de teléfono, categoría, etiquetas.
- [ ] **Política de privacidad** (URL pública) y formulario **Data Safety** (aunque no recojas datos,
      declara tráfico de red y credenciales locales).
- [ ] **Clasificación de contenido** y declaración de cifrado (HTTPS).
- [ ] **App access**: los revisores no tienen tu DSH. Necesitarás un **servidor demo** con token de
      prueba o instrucciones claras; sin esto la revisión puede rechazarse.
- [ ] **Riesgo de política**: apps que son “solo un WebView” pueden rechazarse por funcionalidad
      mínima. Mitiga con valor nativo (biometría, QR, notificaciones, multi-PC, atajos).
- [ ] Pruebas internas/cerradas antes de producción (track de testing).

---

## 5. Legal y marca

- [ ] Nombre: evita implicar afiliación oficial. Ej.: **“DSH Remote (no oficial)”**.
- [ ] La licencia MIT de DSH cubre el **código**, no la **marca** “DeepSeek Harness”.
- [ ] Incluir `THIRD_PARTY_NOTICES` (Capacitor MIT, plugins, DSH MIT).
- [ ] Aviso de “developer preview / sin garantías” y términos de uso.
- [ ] No incluir logos de DeepSeek sin permiso; un icono propio (“DSH”) es más seguro.

---

## 6. Red y onboarding para terceros

- [ ] Guía paso a paso: instalar DSH en el PC → `start-mobile` → instalar Tailscale → escanear QR.
- [ ] Alternativas si no quieren Tailscale: LAN con `--host 192.168.x.x`, o Cloudflare Tunnel con Access.
- [ ] Decidir si habrá **relay/back-end propio** (cuentas, túneles, push). Es un proyecto aparte:
      coste de servidores, autenticación, abuso, privacidad.
- [ ] Notificaciones push: requieren FCM + backend que escuche eventos de DSH (fase 2).

---

## 7. Soporte y operación

- [ ] Repo público + issues + changelog.
- [ ] Web de documentación (o README + wiki).
- [ ] Crash reporting opcional (Firebase Crashlytics) con consentimiento.
- [ ] Política de actualizaciones y matriz de compatibilidad DSH.

---

## 8. Plan por fases

| Fase | Alcance | Tiempo estimado |
|---|---|---|
| **1. Early adopters (sideload)** | allowlist `*`, helper QR Node, deep link, APK release firmado, README/guía | 2-4 días |
| **2. Play internal/closed** | AAB, keystore/Play Signing, ficha, privacidad, data safety, servidor demo, i18n | 1-2 semanas + revisión |
| **3. Público** | onboarding wizard, multi-PC, reconexión, notificaciones/push, soporte, posible relay | 4-8 semanas |

Coste mínimo: **25 USD** (Play) + dominio/privacidad si quieres URL propia. iOS añade 99 EUR/año + Mac.

---

## 9. Lo que ya está resuelto

- WebView con DSH real funcionando (probado en emulador y en tu móvil).
- Emparejamiento por QR + token/cookie, plugin nativo `OpenUrl` (fix SameSite).
- Biometría (corregida; reinstalar APK).
- HTTPS vía Tailscale Serve + QR.
- Iconos, splash, build reproducible con Gradle.