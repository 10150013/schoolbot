# Fusion Gyms: faster check-in for members

**The idea:** a member double-clicks their iPhone side button (or double-taps the screen in the app) and their check-in barcode pops up, like a credit card. No opening the app and tapping through to Key Tag.

## What already works (live demo)
A working demo is at https://10150013.github.io/schoolbot/?code=A3490EANV6MAP&name=Demo
Open it on a phone and double-tap the screen. The barcode is a standard Code 128, the same type as the current Key Tag barcode.

## Two ways to roll it out
1. **Web app (free):** members open a link and add it to their home screen. Double-tap shows the barcode. Works offline.
2. **Apple Wallet pass (best):** each member gets a card in Apple Wallet. Double-clicking the side button shows it, even from the lock screen. Needs an Apple Developer account ($99/year) and a way to send each member their pass.

## What we need from the gym
- Each member's barcode value (the code shown on their Key Tag), or a way to get it from your member system.
- Which system the gym app runs on (the app vendor), so the passes can be handed out automatically.
- Optional: the Fusion Gyms logo, for the pass and app icon.

## Notes
- The demo does not connect to your member database yet. Members type their own code, or open a link that fills it in.
- Code and setup steps: https://github.com/10150013/schoolbot
