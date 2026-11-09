// Usage: node make-pass.mjs "Jane Doe" A3490EANV6MAP
// Needs certs/ and env vars (see README.md). Writes out/<code>.pkpass
import { PKPass } from "passkit-generator";
import fs from "node:fs";

const [name, code] = process.argv.slice(2);
if (!name || !code) { console.error('Usage: node make-pass.mjs "Full Name" MEMBERCODE'); process.exit(1); }
const env = k => { const v = process.env[k]; if (!v) { console.error("Missing env var " + k + " (see README.md)"); process.exit(1); } return v; };
const passTypeIdentifier = env("PASS_TYPE_ID"), teamIdentifier = env("APPLE_TEAM_ID");

const pass = await PKPass.from(
  {
    model: new URL("./model.pass", import.meta.url).pathname,
    certificates: {
      wwdr: fs.readFileSync("certs/wwdr.pem"),
      signerCert: fs.readFileSync("certs/signerCert.pem"),
      signerKey: fs.readFileSync("certs/signerKey.pem"),
      signerKeyPassphrase: process.env.KEY_PASSPHRASE,
    },
  },
  { passTypeIdentifier, teamIdentifier, serialNumber: code }
);
pass.primaryFields.push({ key: "name", label: "MEMBER", value: name });
pass.secondaryFields.push({ key: "code", label: "MEMBER NUMBER", value: code });
pass.setBarcodes({ message: code, format: "PKBarcodeFormatCode128", altText: code });

fs.mkdirSync("out", { recursive: true });
const file = `out/${code}.pkpass`;
fs.writeFileSync(file, pass.getAsBuffer());
console.log("Wrote " + file);
