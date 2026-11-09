# Fusion Gyms Apple Wallet passes

Members add their card to Apple Wallet, then double-click the side button to show it.

## One-time setup (needs an Apple Developer account, $99/yr)
1. developer.apple.com → Certificates, IDs & Profiles → Identifiers → **Pass Type IDs** → create e.g. `pass.com.fusiongyms.member`.
2. Create a certificate for it, download it, and export key + cert as `.p12` from Keychain.
3. Convert and put in `wallet/certs/`:
   ```
   openssl pkcs12 -in pass.p12 -clcerts -nokeys -out certs/signerCert.pem
   openssl pkcs12 -in pass.p12 -nocerts -out certs/signerKey.pem
   ```
   Download Apple's **WWDR G4** certificate (apple.com/certificateauthority), convert it to PEM → `certs/wwdr.pem`.
4. `export PASS_TYPE_ID=pass.com.fusiongyms.member APPLE_TEAM_ID=<your team id> KEY_PASSPHRASE=<key password>`

## Make a pass
```
cd wallet
npm install
node make-pass.mjs "Jane Doe" A3490EANV6MAP
```
Email `out/A3490EANV6MAP.pkpass` to the member. Opening it on an iPhone offers **Add to Apple Wallet**.
Never commit `certs/` or `out/`.
