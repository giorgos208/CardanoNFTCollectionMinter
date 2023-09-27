from blockfrost import BlockFrostApi, ApiError, ApiUrls
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
blockfrost_key = os.getenv("BLOCK_FROST_KEY")
mint_price = str(int(os.getenv("MINT_PRICE")) * 1_000_000)
policy_id = ""
asset_name = ""
full_hex_name = f"{policy_id}{asset_name}"

while True:
    # Check if exit is requested
    with open("code/enable_exit.txt", 'r') as b:
        exit_flag = b.read().strip().lower() == 'true'
    
    if exit_flag:
        exit("Exit requested")

    # Read old addresses
    with open("code/addresses_we_own_NFTs.txt", 'r') as r:
        old_addresses = r.read().strip()

    if old_addresses:
        exit("You still haven't satisfied all the previous minters.")
    
    print("\nStill polling for incoming transactions...")
    time.sleep(60)

    # Read start block and listener address
    with open("code/satisfied_till_block.txt", 'r') as h:
        start_block = h.read().strip()
    
    with open("keys/address.txt", 'r') as h:
        listener = h.read().strip()

    # Initialize API
    api = BlockFrostApi(project_id=blockfrost_key, base_url=ApiUrls.mainnet.value)
    
    try:
        saved_tx_ids = []
        tx_ids = api.address_transactions(listener, start_block)
        
        for i in tx_ids:
            saved_tx_ids.append(i)

        if saved_tx_ids:
            satisfied_till_block = saved_tx_ids[-1].block_height
            print(f"I collected {len(saved_tx_ids)} transaction IDs till block {satisfied_till_block}")

            addresses_that_sent_ADA = []
            
            for tx in saved_tx_ids:
                utxos = api.transaction_utxos(tx.tx_hash)
                
                for u in utxos.outputs:
                    conditions_met = (
                        u.address == listener and 
                        u.amount[0].quantity == mint_price and
                        len(u.amount) >= 2 and
                        u.amount[1].unit == full_hex_name and 
                        u.amount[1].quantity == "10000000000"
                    )
                    if conditions_met:
                        addresses_that_sent_ADA.append(utxos.inputs[0].address)

            print(addresses_that_sent_ADA)

            with open("code/satisfied_till_block.txt", 'w') as t:
                t.write(str(satisfied_till_block + 1))

            with open("code/addresses_we_own_NFTs.txt", 'w') as q:
                for a in addresses_that_sent_ADA:
                    q.write(f"{a}\n")

        else:
            print(f"No new transactions found after the block you specified: {start_block}")

    except ApiError as e:
        print(e)
