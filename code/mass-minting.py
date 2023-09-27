from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
from dotenv import load_dotenv
from pycardano import *
import json
import time
import pathlib
import math

# Load environment variables
load_dotenv()

# Initialize global variables
blockfrost_key = os.getenv("BLOCK_FROST_KEY")
mint_price = str(int(os.getenv("MINT_PRICE")) * 1000 * 1000)
policy_id = ""
asset_name = ""
full_hex_name = policy_id + asset_name
collection_size = int(os.getenv("COLLECTION_SIZE"))
is_sold_out = False

# Load metadata
with open('assets/metadata/_metadata5.json') as k:
    meta_data = json.load(k)

# Function to load or create key pairs
def load_or_create_key_pair(base_dir, base_name):
    skey_path = base_dir / f"{base_name}.skey"
    vkey_path = base_dir / f"{base_name}.vkey"

    # Check if key files exist
    if skey_path.exists():
        skey = PaymentSigningKey.load(str(skey_path))
        vkey = PaymentVerificationKey.from_signing_key(skey)
        print("Found MAINNET/keys")
    else:
        print("I shouldn't be here")
        key_pair = PaymentKeyPair.generate()
        key_pair.signing_key.save(str(skey_path))
        key_pair.verification_key.save(str(vkey_path))
        skey = key_pair.signing_key
        vkey = key_pair.verification_key

    return skey, vkey

# Function to handle refunds
def refund(address_to_refund, values_to_refund):
    print("Refund mechanism initiated.")
    print(f"Attempting to refund to address: {address_to_refund}")
    print(f"Refunding {len(values_to_refund[0])} items: {values_to_refund}")

    BLOCK_FROST_PROJECT_ID = blockfrost_key
    NETWORK = Network.MAINNET
    sk = PaymentSigningKey.load("keys/payment.skey")
    vk = PaymentVerificationKey.from_signing_key(sk)
    address = Address(vk.hash(), None, NETWORK)

    while True:
        try:
            context = BlockFrostChainContext(BLOCK_FROST_PROJECT_ID, base_url=ApiUrls.mainnet.value)
            builder = TransactionBuilder(context)
            builder.add_input_address(address)

            # Build transaction output
            builder.add_output(
                TransactionOutput(
                    Address.from_primitive(address_to_refund),
                    Value.from_primitive(
                        [
                            1700000,
                            {
                                bytes.fromhex("8654e8b350e298c80d2451beb5ed80fc9eee9f38ce6b039fb8706bc3"): {
                                    b"LOBSTER": int(values_to_refund[0][1])
                                }
                            },
                        ]
                    ),
                )
            )

            # Sign and submit the transaction
            signed_tx = builder.build_and_sign([sk], change_address=address)
            print(f"Transaction ID: {signed_tx.id}")
            context.submit_tx(signed_tx.to_cbor())
            break

        except ApiError as e:
            print("Submission too fast, retrying later.")
            print(e)
            time.sleep(5)


def MintNFTs(array, values):
    global is_sold_out  # Using global variables is generally not recommended but leaving it as is.
    
    # Initialize project and network settings
    PROJECT_ROOT = ""
    root = pathlib.Path(PROJECT_ROOT)
    BLOCK_FROST_PROJECT_ID = blockfrost_key
    NETWORK = Network.MAINNET
    
    # Create necessary directories
    root.mkdir(parents=True, exist_ok=True)
    key_dir = root / "keys"
    key_dir.mkdir(exist_ok=True)
    
    # Load or create keys for payment and address
    payment_skey, payment_vkey = load_or_create_key_pair(key_dir, "payment")
    address = Address(payment_vkey.hash(), network=NETWORK)
    
    # Generate and load policy keys and scripts
    policy_skey, policy_vkey = load_or_create_key_pair(key_dir, "policy")
    
    with open(root / "policy.script") as f:
        data = f.read()
    f.close()
    
    # Generate policy dictionary and hashes
    dictionary_input = json.loads(data)
    policy = ScriptAll.from_dict(dictionary_input)
    policy_id = policy.hash()
    
    # Start minting loop
    for p in range(0, len(array)):
        print(f"Left to mint: {len(array)}")
        
        address_to_mint = array.pop()
        nfts_ordered = values.pop()
        print(f"Will mint on this address: {address_to_mint} they paid for: {nfts_ordered} NFTs")
        
        # Initialize asset containers and metadata attributes
        my_asset = Asset()
        
        # Open last minted information
        with open("code/last_minted.txt", 'r') as h:
            last_minted = int(h.read())
        h.close()
        
        # Check if the collection is sold out
        if last_minted >= collection_size:
            is_sold_out = True
            print("Collection sold out")
            exit("Will never refund")
            refund(address_to_mint, values)
            continue

        # Generate NFT names based on the metadata
        nfts = [AssetName(bytes(meta_data[last_minted + k]["ID"], 'UTF-8')) for k in range(0, nfts_ordered)]
        
        # Populate asset container
        for k in range(0, nfts_ordered):
            my_asset[nfts[k]] = 1
            
        # Create MultiAsset container
        my_nft = MultiAsset()
        my_nft[policy_id] = my_asset

        # Generate NFT metadata
        nft_dict = {
            meta_data[last_minted + k]["ID"]: {
                "Description": meta_data[last_minted + k]["description"],
                "name": meta_data[last_minted + k]["name"],
                # ... Add more attributes here
                "Speed": meta_data[last_minted + k]["Speed"],
                "twitter": meta_data[last_minted + k]["twitter"],
            } 
            for k in range(0, nfts_ordered)
        }

        # Create metadata for minting
        metadata = {
            721: {
                policy_id.payload.hex(): nft_dict
            }
        }

        #print(metadata)
        # Place metadata in AuxiliaryData, the format acceptable by a transaction
    auxiliary_data = AuxiliaryData(AlonzoMetadata(metadata=Metadata(metadata)))

    # Main loop to handle transaction submission
    while True:
        time.sleep(10)  # Pause for 10 seconds before each iteration
        
        # Initialize chain context
        chain_context = BlockFrostChainContext(
            project_id=BLOCK_FROST_PROJECT_ID,
            base_url=ApiUrls.mainnet.value
        )
        
        # Initialize transaction builder
        builder = TransactionBuilder(chain_context)
        
        # Add input address to the transaction
        builder.add_input_address(address)
        
        # Set Time to Live (TTL) for the transaction (1-year locked-policy)
        must_before_slot = InvalidHereAfter(chain_context.last_block_slot + 10000)
        builder.ttl = must_before_slot.after
        
        # Define the NFT to be minted
        builder.mint = my_nft
        
        # Attach native scripts to the transaction
        builder.native_scripts = native_scripts
        
        # Attach metadata to the transaction
        builder.auxiliary_data = auxiliary_data
        
        # Calculate the minimum amount of lovelace required to hold the NFT
        min_val = min_lovelace(
            chain_context,
            output=TransactionOutput(Address.from_primitive(address_to_mint), Value(0, my_nft))
        )
        
        # Add an output address for the NFT
        builder.add_output(TransactionOutput(Address.from_primitive(address_to_mint), Value(min_val, my_nft)))

        # Build and sign the transaction
        signed_tx = builder.build_and_sign([payment_skey, policy_skey], change_address=address)

        print("\n\nTrying to submit transaction..\n\n")

        try:
            # Submit the transaction
            chain_context.submit_tx(signed_tx.to_cbor())
        except ApiError as e:
            print("Too fast, try again later")
            print(e)
            time.sleep(10)

        # Validation loop for transaction submission
        print("Trying to validate that my transaction had been submitted...")
        tries = 0
        is_submitted = False
        while True:
            tries += 1
            try:
                # Check the transaction
                temp_api = BlockFrostApi(
                    project_id=blockfrost_key,
                    base_url=ApiUrls.mainnet.value
                )
                api_return = temp_api.transaction_utxos(str(signed_tx.id))
                is_submitted = True
                break
            except ApiError as e:
                print(f"{e}, Error while checking for legitimacy of the SUBMITTED transaction hash. Waiting 30 seconds.. {signed_tx.id}")
                time.sleep(30)
                if tries >= 15:
                    print("\nTransaction FAILED.\n")
                    break
        if is_submitted:
            print("\n\nSuccessful submission!", signed_tx.id, "\n")

        # Update the last minted NFT count
        last_minted = last_minted + nfts_ordered
        with open("code/last_minted.txt", 'w') as t:
            t.write(str(last_minted))
        print(f"Minted an NFT, now last minted is {last_minted}")

#################################
# Infinite loop to monitor transactions and actions
while True:
    
    # Read exit flag
    with open("code/enable_exit.txt", 'r') as b:
        temp = b.read()
        exit_flag = temp.lower() == "true"
    
    # Exit if the flag is set
    if exit_flag:
        exit("Exit requested")
    
    # Check old addresses
    with open("code/addresses_we_own_NFTs.txt", 'r') as r:
        old_addresses = r.read()

    if len(old_addresses) != 0:
        exit("You still haven't satisfied all the previous minters.")

    print("\nStill polling for incoming transactions..")
    time.sleep(35)
    
    # Read starting block and transaction index
    with open("code/satisfied_till_block.txt", 'r') as h:
        start_block = h.read()
    with open("code/satisfied_till_index.txt", 'r') as n:
        tx_index = n.read()

    # Read listener address
    with open("keys/address.txt", 'r') as h:
        listener = h.read()
    
    # Initialize BlockFrost API
    api = BlockFrostApi(
        project_id=blockfrost_key,
        base_url=ApiUrls.mainnet.value
    )

    try:
        saved_tx_ids = []
        
        # Fetch transactions for the address
        tx_ids = api.address_transactions(listener, f"{start_block}:{tx_index}")
        
        for i in tx_ids:
            saved_tx_ids.append(i)

        if len(saved_tx_ids) != 0:
            print(f"Searching for transactions at: {start_block}:{tx_index}")
            
            # Update the latest block and transaction index
            satisfied_till_block = saved_tx_ids[-1].block_height
            tx_index_last = saved_tx_ids[-1].tx_index
            print(f"I collected {len(saved_tx_ids)} transaction IDs till block {satisfied_till_block} and tx_index={tx_index_last}")

            addresses_that_sent_ADA = []
            values_sent = []
            
            # Iterate through transactions to find relevant addresses and values
            for j in range(len(saved_tx_ids)):
                utxos = api.transaction_utxos(saved_tx_ids[j].tx_hash)
                
                for u in utxos.outputs:
                    if u.address == listener and utxos.inputs[0].address != listener and int(u.amount[0].quantity) >= 2000000:
                        addresses_that_sent_ADA.append(utxos.inputs[0].address)
                        values_sent.append(min(math.floor(int(u.amount[0].quantity) // 2000000), 10))
            
            # Mint NFTs if there are valid addresses
            if len(addresses_that_sent_ADA) > 0:
                MintNFTs(addresses_that_sent_ADA, values_sent)

            # Update stored block and transaction index
            with open("code/satisfied_till_block.txt", 'w') as t:
                t.write(str(satisfied_till_block))
            with open("code/satisfied_till_index.txt", 'w') as m:
                m.write(str(tx_index_last + 1))
            
            # Update list of addresses owning NFTs
            with open("code/addresses_we_own_NFTs.txt", 'w') as q:
                for a in addresses_that_sent_ADA:
                    q.write(f'{a}\n')
        else:
            print(f"No new transactions found after the block you specified, {start_block}")
    
    except ApiError as e:
        print(e)
