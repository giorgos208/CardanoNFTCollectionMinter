from blockfrost import ApiUrls, ApiError
from pycardano import *
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
vault_address = os.getenv('VAULT_ADDRESS')
blockfrost_key = os.getenv("BLOCK_FROST_KEY")

# Initialize Cardano network and chain context
network = Network.MAINNET
context = BlockFrostChainContext(blockfrost_key, base_url=ApiUrls.mainnet.value)

# Load signing and verification keys
sk = PaymentSigningKey.load("keys/payment.skey")
vk = PaymentVerificationKey.from_signing_key(sk)
address = Address(vk.hash(), None, network)

# Read addresses from file
with open("code/addresses_we_own_NFTs.txt", 'r') as h:
    addresses = h.readlines()
h.close()

# Exit if no addresses are present
if len(addresses) == 0:
    exit("No address to mint")

# Remove newline characters from addresses
addresses_no_new_line = [a.strip() for a in addresses]

# Loop through addresses to refund
for p in range(len(addresses_no_new_line)):
    print(f"Left to refund: {len(addresses_no_new_line)}")
    
    address_to_refund = addresses_no_new_line.pop()
    print(f"Will refund on this address: {address_to_refund}")

    while True:
        try:
            chain_context = BlockFrostChainContext(
                project_id=blockfrost_key,
                base_url=ApiUrls.mainnet.value,
            )

            # Create and sign transaction
            builder = TransactionBuilder(context)
            builder.add_input_address(address)
            builder.add_output(TransactionOutput(
                Address.from_primitive(address_to_refund), 
                Value.from_primitive([3 * 1000 * 1000])
            ))

            signed_tx = builder.build_and_sign([sk], change_address=address)
            print(f"{signed_tx.id}\n############### Submitting transaction ###############")
            context.submit_tx(signed_tx.to_cbor())
            break

        except ApiError as e:
            print(e)
            time.sleep(5)

    # Update file with remaining addresses
    with open("code/addresses_we_own_NFTs.txt", 'w') as g:
        for line in addresses_no_new_line:
            g.write(f"{line}\n")
    g.close()
