from pycardano import Address, Network, PaymentSigningKey, PaymentVerificationKey
import os

# Create 'keys' directory if it does not exist
if not os.path.exists("keys"):
    os.makedirs("keys")

# Generate payment signing key and save it to the 'keys' folder
payment_signing_key = PaymentSigningKey.generate()
payment_signing_key.save("keys/payment.skey")

# Generate payment verification key from the signing key
payment_verification_key = PaymentVerificationKey.from_signing_key(payment_signing_key)
payment_verification_key.save("keys/payment.vkey")

# Set network to MAINNET
network = Network.MAINNET

# Generate address from verification key hash and network
address = Address(payment_part=payment_verification_key.hash(), network=network)

# Write the generated address to a file
with open("keys/address.txt", "w+") as f:
    f.write(str(address))
