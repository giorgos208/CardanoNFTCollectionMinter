# Cardano NFT Collection Minter

## Description

This repository offers a comprehensive solution for minting NFT collections on the Cardano blockchain. It is designed to accommodate a range of use-cases, from testing and simulations to real-world applications.

### Information

1) The system administrator is responsible for creating and funding their own Cardano wallet address. The code for this can be found in the "code" folder.
2) The system administrator can fulfill NFT orders from buyers who send $ADA to the designated wallet address.
3) NFTs are minted based on the corresponding JSON files located in the "assets" folder. The system ensures that there are no duplicate NFTs by removing each minted item from the list.
4) The platform is scalable, capable of minting multiple NFTs to multiple buyers in a single transaction, leveraging Cardano's UTXO model.
