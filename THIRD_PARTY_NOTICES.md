# Third-party notices

DSH Mobile is MIT licensed. It depends on these projects, each with its own license:

| Project | License | Use |
|---|---|---|
| [Capacitor](https://github.com/ionic-team/capacitor) (core, cli, android) | MIT | Native runtime |
| [@capacitor/preferences](https://github.com/ionic-team/capacitor-plugins) | MIT | Local storage |
| [@capacitor/barcode-scanner](https://github.com/ionic-team/capacitor-barcode-scanner) | MIT | QR scanning |
| [@aparajita/capacitor-biometric-auth](https://github.com/aparajita/capacitor-biometric-auth) | MIT | Biometric prompt |
| [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) | MIT | Software this app connects to (not bundled) |

Android transitive dependencies are declared in `android/app/build.gradle` and keep their own licenses. Run `./gradlew app:dependencies` for the full graph.
