from blockfrost import ApiUrls, ApiError
from pycardano import *
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
vault_address = os.getenv('VAULT_ADDRESS')
blockfrost_key = os.getenv("BLOCK_FROST_KEY")

# Initialize asset variables
my_asset = Asset()
tokens = AssetName(bytes("4c4f4253544552", 'UTF-8'))
my_asset[tokens] =   # 20B
my_ft = MultiAsset()

# Set network and context
network = Network.MAINNET
context = BlockFrostChainContext(blockfrost_key, base_url=ApiUrls.mainnet.value)

# Load keys and address
sk = PaymentSigningKey.load("keys/payment.skey")
vk = PaymentVerificationKey.from_signing_key(sk)
address = Address(vk.hash(), None, network)

# Initialize transaction builder
builder = TransactionBuilder(context)
builder.add_input_address(address)

# Add transaction output
builder.add_output(
    TransactionOutput(
        Address.from_primitive(
            ""
        ),
        Value.from_primitive(
            [
                82_000_000,
                {
                    bytes.fromhex(
                        ""  # Policy ID
                    ): {
                        b"": 0  # Asset name and amount
                    }
                },
            ]
        ),
    )
)

# Build and sign transaction
signed_tx = builder.build_and_sign([sk], change_address=address)
print(signed_tx.id)

# Submit transaction
try:
    context.submit_tx(signed_tx.to_cbor())
except ApiError as e:
    print("Too fast, try again later")
    print(e)
