// Sends the store owner a text when a customer places an order.
// Needs these environment variables in Netlify:
//   TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM (your Twilio number), OWNER_PHONE (your cell, e.g. +12155551234)
const clean = (v, n) => String(v || "").replace(/[\r\n]+/g, " ").trim().slice(0, n);

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, body: "Method not allowed" };
  let d;
  try { d = JSON.parse(event.body || "{}"); } catch (e) { return { statusCode: 400, body: "Bad request" }; }

  const street = clean(d.street, 120), city = clean(d.city, 60), zip = clean(d.zip, 10);
  const item = clean(d.item, 80) || "the $70 item";
  const eta = clean(d.eta, 60);
  if (!street || !city || !/^\d{5}$/.test(zip)) return { statusCode: 400, body: "Missing address" };

  const { TWILIO_ACCOUNT_SID: sid, TWILIO_AUTH_TOKEN: token, TWILIO_FROM: from, OWNER_PHONE: to } = process.env;
  if (!sid || !token || !from || !to) return { statusCode: 500, body: "Texting is not set up" };

  const body = `New order: ${item} ($70)\nDeliver to: ${street}, ${city} ${zip}` + (eta ? `\nETA: ${eta}` : "");
  const res = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${sid}/Messages.json`, {
    method: "POST",
    headers: {
      Authorization: "Basic " + Buffer.from(`${sid}:${token}`).toString("base64"),
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ To: to, From: from, Body: body }).toString(),
  });
  if (!res.ok) return { statusCode: 502, body: "Could not send text" };
  return { statusCode: 200, body: "ok" };
};
