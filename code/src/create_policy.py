from pycardano import Address, Network, PaymentSigningKey, PaymentVerificationKey, PaymentKeyPair, ScriptPubkey, ScriptAll, InvalidHereAfter
from blockfrost import ApiUrls, BlockFrostChainContext
import os
import pathlib
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
blockfrost_key = os.getenv("BLOCK_FROST_KEY")

# Set network to MAINNET
NETWORK = Network.MAINNET

# Define directories
PROJECT_ROOT = ""
root = pathlib.Path(PROJECT_ROOT)
root.mkdir(parents=True, exist_ok=True)
key_dir = root / "keys"
key_dir.mkdir(exist_ok=True)

# Function to load or create key pair
def load_or_create_key_pair(base_dir, base_name):
    skey_path = base_dir / f"{base_name}.skey"
    vkey_path = base_dir / f"{base_name}.vkey"

    if skey_path.exists():
        skey = PaymentSigningKey.load(str(skey_path))
        vkey = PaymentVerificationKey.from_signing_key(skey)
        print(f"Keys for {base_name} found.")
    else:
        print(f"Creating keys for {base_name}...")
        key_pair = PaymentKeyPair.generate()
        key_pair.signing_key.save(str(skey_path))
        key_pair.verification_key.save(str(vkey_path))
        skey = key_pair.signing_key
        vkey = key_pair.verification_key

    return skey, vkey

# Load or create payment keys
payment_skey, payment_vkey = load_or_create_key_pair(key_dir, "payment")
address = Address(payment_vkey.hash(), network=NETWORK)

# Load or create policy keys
policy_skey, policy_vkey = load_or_create_key_pair(key_dir, "policy")

# Create policies
pub_key_policy = ScriptPubkey(policy_vkey.hash())

chain_context = BlockFrostChainContext(
    project_id=blockfrost_key,
    base_url=ApiUrls.mainnet.value,
)
must_before_slot = InvalidHereAfter(chain_context.last_block_slot + 30000000)

policy = ScriptAll([pub_key_policy, must_before_slot])
policy_id = policy.hash()

# Save policy ID and script
with open(root / "policy.id", "w") as f:
    f.write(str(policy_id))

with open(root / "policy.script", "w") as h:
    json_object = json.dumps(policy.to_dict())
    h.write(json_object)
    print(json_object)
