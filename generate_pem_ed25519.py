# generate_pem_ed25519.py
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption

# Generate key pair
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Get private key in hex (for .env)
private_bytes = private_key.private_bytes_raw()
private_hex = private_bytes.hex()

# Get public key in PEM format (for Binance)
public_pem = public_key.public_bytes(
    encoding=Encoding.PEM,
    format=PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

print("=" * 70)
print("🔑 ED25519 KEY PAIR - PEM FORMAT (Binance Will Accept)")
print("=" * 70)

print(f"\n📝 PUBLIC KEY (Copy this EXACTLY on Binance):")
print(public_pem)

print(f"\n🔐 PRIVATE KEY (Put in .env):")
print(private_hex)

print("\n" + "=" * 70)
print("⚠️ SAVE PRIVATE KEY NOW! It won't be shown again.")
print("✅ Public key is in PEM format - Binance will accept this.")