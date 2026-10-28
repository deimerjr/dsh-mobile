# Contributing

Thanks for your interest!

## Before you start

- Search existing issues and PRs first.
- This is an **unofficial** client for DeepSeek Harness. Do not report app bugs to DeepSeek.
- DSH is a developer preview: breaking changes may need app changes.

## Development

```bash
npm install
npx cap sync android
cd android
./gradlew assembleDebug
```

- Web shell: `www/index.html` (plain HTML/CSS/JS, no build step).
- Native code: `android/app/src/main/java/io/github/deimerjr/dshmobile/`.
- After editing `www/` run `npx cap sync android` before building.
- Tested on Android 16 (API 36) emulator and a Galaxy S25 Ultra.

## Pull requests

- Keep changes focused and explain why.
- If you touch native navigation or biometrics, test pairing on a real device.
- Do not commit keystores, tokens, personal hostnames or APKs.

## Security

Report vulnerabilities privately via a GitHub security advisory, not a public issue.
