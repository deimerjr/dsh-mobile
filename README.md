# DSH Mobile

An unofficial Android client for **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** (DSH): it opens the official DSH Web UI in a native WebView and adds QR pairing and an optional biometric lock.

> **Not affiliated with DeepSeek.** The name is used nominatively to describe the software this app connects to. DSH is a *developer preview* and changes often. The APK in Releases is a **debug build** for personal/sideload use, not a Play Store app.

<p align="center">
  <img src="docs/screenshots/pairing.png" width="260" alt="Pairing screen">
  <img src="docs/screenshots/dsh.png" width="260" alt="DSH inside the app">
</p>

## Contents

1. [What it is and what it is not](#1-what-it-is-and-what-it-is-not)
2. [How it works](#2-how-it-works)
3. [Requirements](#3-requirements)
4. [Install the app](#4-install-the-app)
5. [Prepare DSH on your computer](#5-prepare-dsh-on-your-computer)
6. [Expose DSH to the phone](#6-expose-dsh-to-the-phone)
7. [Pair the app](#7-pair-the-app)
8. [Verify](#8-verify)
9. [Troubleshooting](#9-troubleshooting)
10. [Security and privacy](#10-security-and-privacy)
11. [Limitations](#11-limitations)
12. [FAQ](#12-faq)
13. [Build from source](#13-build-from-source)
14. [Project layout](#14-project-layout)

---

## 1. What it is and what it is not

**It is** a thin shell: the real DSH Web UI is served by **your computer** and rendered in an Android WebView. The app only stores the server URL, pairs with a QR code and optionally asks for your fingerprint before connecting.

**It is not** a mobile reimplementation of DSH, and **it does not include Tailscale**. There is no DSH backend, no model API key and no VPN inside the APK.

---

## 2. How it works

```text
Phone                                      Computer
+---------------------------+              +--------------------------------------+
|  DSH Mobile (WebView)     |   HTTPS      |  Tailscale (WireGuard)               |
|      |                    |   over       |      |                               |
|      +--> tailnet URL     |   tailnet    |      +--> tailscale serve :443        |
|                           |              |                |                     |
+---------------------------+              |                +--> 127.0.0.1:3080   |
                                           |                        DSH web      |
                                           +--------------------------------------+
```

Key points:

- The app needs a URL reachable from the phone. **Tailscale is recommended**, but the app is network-agnostic: LAN or any HTTPS tunnel works too.
- Tailscale must run on **both** devices, and `tailscale serve` (or another HTTPS proxy) exposes the loopback DSH.
- DSH's session cookie uses `SameSite=Strict`. That is why the app navigates through a **native plugin** (`WebView.loadUrl`) instead of page JavaScript. If you fork it, do not replace that with `location.replace()` or the token exchange will fail.

---

## 3. Requirements

### Phone

| Requirement | Notes |
|---|---|
| Android 8.0+ (API 26) | Target SDK 36 |
| Camera | Only to scan the pairing QR; you can paste the URL instead |
| Tailscale app (recommended) | Log in with the **same account** as the computer. Only needed if you use Tailscale |

### Computer (runs DSH)

| Requirement | Notes |
|---|---|
| Node.js **24.9+** | DSH's own minimum |
| DSH from npm | `npx @deepseek-ai/dsh web` downloads and runs it |
| Working DSH setup | Model/API key configured; otherwise the UI loads but cannot chat |
| Network exposure | Tailscale Serve, LAN bind or a TLS tunnel (see below) |
| Optional: Tailscale | Installed and logged in on the same tailnet as the phone |
| Optional: Tailscale Serve | **Disabled by default.** Must be enabled for the tailnet in the Tailscale admin console |

### Building the APK (only if you do not use Releases)

| Requirement | Notes |
|---|---|
| Node.js 24.9+ | Capacitor and npm scripts |
| JDK 21 | Gradle runs on it |
| Android SDK | Platform 36 + build-tools 36.x |
| Gradle | Provided by the wrapper (9.0.0) |
| NDK | **Not required** |

---

## 4. Install the app

### Option A: prebuilt APK (fastest)

1. Open **[Releases](https://github.com/deimerjr/dsh-mobile/releases)** and download `dsh-mobile-0.1.0-debug.apk`.
2. On the phone, allow installing unknown apps for your file manager/browser and open the APK.
3. If you previously installed a build with a different app id, uninstall it first: it is a separate package.

### Option B: build it yourself

See [Build from source](#13-build-from-source).

---

## 5. Prepare DSH on your computer

1. Install **Node.js 24.9+** (`node --version`).
2. Start the DSH Web UI on loopback:

   ```bash
   npx @deepseek-ai/dsh web --no-open --port 3080
   ```

   The first run downloads DSH. Wait for `dsh web: http://127.0.0.1:3080/?token=...`. **Keep that terminal open**: it is the server.

3. Open that URL on the computer browser and confirm DSH works (model configured, workspace selected).

> DSH stores sessions and credentials in `~/.dsh`, shared with other DSH profiles on the same machine.

---

## 6. Expose DSH to the phone

Pick **one** option. Tailscale is recommended: it encrypts traffic and does not expose DSH to the Internet.

### Option 1: Tailscale + Tailscale Serve (recommended)

Once:

1. Install **Tailscale** on the computer and the phone; log in with the **same account**.
2. In the Tailscale admin console, enable **Serve** for the tailnet (it is off by default; the command prints the activation link when off).
3. Get the machine's tailnet name:

   ```bash
   # macOS / Linux
   tailscale status --json | jq -r .Self.DNSName

   # Windows PowerShell
   (tailscale status --json | ConvertFrom-Json).Self.DNSName
   ```

   It looks like `my-pc.tailXXXX.ts.net` (without the trailing dot).

4. Publish loopback DSH over HTTPS:

   ```bash
   tailscale serve --bg --https=443 http://127.0.0.1:3080
   tailscale serve status     # should show https://<your-host> -> http://127.0.0.1:3080
   ```

5. Restart DSH so it trusts the public host and advertises the HTTPS URL:

   ```bash
   npx @deepseek-ai/dsh web --no-open --port 3080 ^
     --trusted-host <your-host> ^
     --public-url https://<your-host>/
   ```

   (On macOS/Linux use a backslash instead of `^`.) DSH now prints `dsh web: https://<your-host>/?token=...`.

> Why `--trusted-host`? DSH checks the HTTP `Host` header. Through Serve it is the tailnet name, so DSH must accept it. `--public-url` only changes what DSH prints and advertises.
>
> On Windows you usually **cannot** open `https://<your-host>/` from the same PC. Test from the phone.

### Option 2: LAN (same Wi-Fi)

```bash
npx @deepseek-ai/dsh web --no-open --port 3080 --host 192.168.1.50
```

Use the computer's LAN IPv4. Allow TCP 3080 in the firewall and open `http://192.168.1.50:3080/?token=...` on the phone. Cleartext, same network only.

### Option 3: HTTPS tunnel

Any tunnel pointing at `http://127.0.0.1:3080`, for example:

```bash
cloudflared tunnel --url http://127.0.0.1:3080
```

Then restart DSH with `--trusted-host <tunnel-host> --public-url https://<tunnel-host>/`. Protect the tunnel with the provider's access control: the URL token is a credential.

---

## 7. Pair the app

### Helper (prints a QR in the terminal)

```bash
npm install
npm run pair -- --host 127.0.0.1 --port 3080 ^
  --trusted-host <your-host> --public-url https://<your-host>/
```

(Windows `^`, macOS/Linux backslash.) It does **not** configure Tailscale Serve; do the previous section first.

### Manual

1. Copy the `dsh web: https://.../?token=...` URL printed by DSH.
2. Open DSH Mobile, paste it in **Emparejar** and tap **Guardar y conectar**.
3. Or generate a QR with any tool and scan it.

### What is stored

The app stores the URL **including the token** in private storage so reconnecting works. The token is exchanged for an `HttpOnly` cookie on first load. When DSH restarts the token rotates: open the app, tap **Olvidar** and scan the new QR.

---

## 8. Verify

1. On the phone, with Tailscale enabled, open the URL **in Chrome first**. If Chrome cannot load it, the app cannot either.
2. Open DSH Mobile and tap **Conectar**; approve biometrics if prompted.
3. You should see the DSH chat UI. Pick a workspace and send a test message.

---

## 9. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `dsh web authentication required` | Token expired or DSH restarted. App: **Olvidar** and scan the new QR. |
| Chrome cannot open `https://<host>/` | Tailscale off on the phone, Serve not configured, wrong hostname or DSH not listening on 127.0.0.1. Check `tailscale serve status` and `tailscale ping <phone>`. |
| `ERR_CONNECTION_REFUSED` or timeout on LAN | Firewall blocking 3080, wrong IP, or DSH bound to 127.0.0.1 instead of the LAN IP. |
| `403` / forbidden | `--trusted-host` does not match the hostname in the URL (tailnet vs. tunnel name). |
| Stuck on splash | First WebView start is slow; wait and reopen. |
| Biometrics cancelled | Tap **Conectar** again; **Probar** tests the prompt without connecting. Technical failures are skipped; only a user cancel blocks. |
| QR does not scan | Missing camera permission or no camera. Paste the URL manually. |
| `tailscale serve` says it is not enabled | Enable Serve for the tailnet in the admin console (the command prints the link), then retry. |

---

## 10. Security and privacy

- The URL/QR contains a **process token**. Treat it like a password and do not post screenshots that show it.
- Token and URL live in the app's private storage. **No analytics, accounts, telemetry or third-party servers**: traffic goes only to the URL you pair.
- Cleartext HTTP is allowed because LAN/tailnet setup often uses IPs. Prefer HTTPS.
- Biometrics are a convenience lock, not a security boundary: the real credential is the DSH cookie.
- Anyone who can reach your DSH URL and token can control your agents. Keep Tailscale ACLs strict and do not expose DSH publicly without an access-control layer.

---

## 11. Limitations

- The DSH Web UI is desktop-oriented; on a phone you get a desktop-ish layout.
- No push notifications.
- Android back leaves the remote view; reopen the app to reach pairing.
- No iOS build.
- One server at a time, no multi-PC switcher.
- The Releases APK is **debug-signed**; it cannot update over a release-signed build.
- DSH is a developer preview; breaking changes may need an app update.

---

## 12. FAQ

**Does the app include Tailscale?** No. It uses the Tailscale app on the phone and the computer. The APK has no VPN, no Tailscale SDK and no account login.

**Can I use it without Tailscale?** Yes: LAN bind or an HTTPS tunnel.

**Does DSH run on the phone?** No. The computer runs DSH; the phone is a remote control.

**Can I connect to several PCs?** Not yet; one server is stored at a time.

**Is it on Google Play?** No. The current build is a sideload debug APK.

**Why is my first message not answered?** Check that DSH itself works on the computer (model/API key configured) and that a workspace is selected.

---

## 13. Build from source

Prerequisites: Node.js 24.9+, JDK 21, Android SDK platform 36 and build-tools 36.x (set `ANDROID_HOME`). No NDK.

```bash
git clone https://github.com/deimerjr/dsh-mobile.git
cd dsh-mobile
npm install
npx cap sync android
cd android
./gradlew assembleDebug        # Windows: gradlew.bat assembleDebug
```

APK: `android/app/build/outputs/apk/debug/app-debug.apk`.

The app id is `io.github.deimerjr.dshmobile`. If you fork and publish, change it in `capacitor.config.json`, `android/app/build.gradle`, `strings.xml` and the Java package, or installs will conflict.

---

## 14. Project layout

```text
www/index.html                 pairing shell (HTML/CSS/JS, no bundler)
capacitor.config.json          app id, web dir, navigation allowlist
tools/pair.mjs                 QR pairing helper (Node)
tools/make-icons.py            launcher icon / splash generator
android/                       Capacitor Android project
  app/src/main/java/io/github/deimerjr/dshmobile/
    MainActivity.java          registers OpenUrlPlugin
    OpenUrlPlugin.java         native navigation (SameSite fix)
docs/screenshots/              screenshots used in this README
```

## Contributing and license

Issues and PRs are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). MIT license ([LICENSE](LICENSE)); third-party notices in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Leer en español](README.es.md)
