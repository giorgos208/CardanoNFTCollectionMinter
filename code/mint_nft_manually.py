import json
import os
import pathlib
import time
from blockfrost import ApiUrls, ApiError
from pycardano import *

# Load environment variables
load_dotenv()
blockfrost_key = os.getenv("BLOCK_FROST_KEY")
collection_size = int(os.getenv("COLLECTION_SIZE"))

# Initialize constants
BLOCK_FROST_PROJECT_ID = blockfrost_key
NETWORK = Network.MAINNET
PROJECT_ROOT = pathlib.Path("")

# Create necessary directories
PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
key_dir = PROJECT_ROOT / "keys"
key_dir.mkdir(exist_ok=True)


def load_or_create_key_pair(base_dir, base_name):
    skey_path = base_dir / f"{base_name}.skey"
    vkey_path = base_dir / f"{base_name}.vkey"

    if skey_path.exists():
        skey = PaymentSigningKey.load(str(skey_path))
        vkey = PaymentVerificationKey.from_signing_key(skey)
        print("Found keys")
    else:
        print("I shouldn't be here")
        key_pair = PaymentKeyPair.generate()
        key_pair.signing_key.save(str(skey_path))
        key_pair.verification_key.save(str(vkey_path))
        skey = key_pair.signing_key
        vkey = key_pair.verification_key

    return skey, vkey


# Initialize payment and policy keys
payment_skey, payment_vkey = load_or_create_key_pair(key_dir, "payment")
policy_skey, policy_vkey = load_or_create_key_pair(key_dir, "policy")

# Initialize payment address
address = Address(payment_vkey.hash(), network=NETWORK)

# Load and parse policy script
with open(root / "policy.script") as f:
    policy_data = json.load(f)
policy = ScriptAll.from_dict(policy_data)

# Calculate policy ID
policy_id = policy.hash()

# Loop through addresses
for p in range(len(addresses_no_new_line)):
    print(f"Left to mint: {len(addresses_no_new_line)}")
    
    address_to_mint = addresses_no_new_line.pop()
    print(f"Will mint on this address: {address_to_mint}")

    # Load metadata and last minted value
    metadata_data = load_asset_metadata('assets/metadata/final_metadata.json')
    last_minted = read_last_minted_value("code/last_minted.txt")

    if last_minted >= collection_size:
        exit("Collection sold out")

    # Define NFT asset
    nft_name = AssetName(bytes(metadata_data[last_minted]["id"], 'UTF-8'))
    my_asset = {nft_name: 1}
    my_nft = {policy_id: my_asset}

    # Define metadata
    nft_data = metadata_data[last_minted]
    metadata = {
        721: {
            policy_id.payload.hex(): {
                nft_data["id"]: {
                    "Description": nft_data["Description"],
                    "name": nft_data["name"],
                    "image": nft_data["image"],
                    "artist": nft_data["Artist"],
                    "twitter": nft_data["Twitter"],
                    "signature": nft_data["signature"],
                    "minted by": nft_data["Mintedby"]
                }
            }
        }
    }

    # Attach script to transaction
    native_scripts = [policy]

    # Place metadata in AuxiliaryData, the format acceptable by a transaction.
    # Initialize Auxiliary Data
auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=Metadata(metadata)))

while True:
    try:
        # Initialize chain context and transaction builder
        chain_context = BlockFrostChainContext(
            project_id=BLOCK_FROST_PROJECT_ID,
            base_url=ApiUrls.mainnet.value
        )
        builder = TransactionBuilder(chain_context)

        # Setup transaction builder
        builder.add_input_address(address)
        must_before_slot = InvalidHereAfter(chain_context.last_block_slot + 10000)  # 1 year locked-policy
        builder.ttl = must_before_slot.after
        builder.mint = my_nft
        builder.native_scripts = native_scripts
        builder.auxiliary_data = auxiliary_data

        # Calculate minimum lovelace needed for transaction
        min_val = min_lovelace(
            chain_context,
            output=TransactionOutput(Address.from_primitive(address_to_mint), Value(0, my_nft))
        )

        # Add transaction output
        builder.add_output(TransactionOutput(Address.from_primitive(address_to_mint), Value(min_val, my_nft)))

        # Sign and submit transaction
        signed_tx = builder.build_and_sign([payment_skey, policy_skey], change_address=address)
        print("############### Transaction created ###############")
        print("############### Submitting transaction ###############")
        chain_context.submit_tx(signed_tx.to_cbor())
        break
    except ApiError as e:
        print(e)
        time.sleep(5)

# Update last_minted value
last_minted += 1
with open("code/last_minted.txt", 'w') as t:
    t.write(str(last_minted))

# Update addresses file
with open("code/addresses_we_own_NFTs.txt", 'w') as g:
    for line in addresses_no_new_line:
        g.write(f'{str(line)}\n')

print(f"Minted an NFT, now last minted is {last_minted}")
