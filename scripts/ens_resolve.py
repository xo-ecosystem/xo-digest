from web3 import Web3
from ens import ENS

w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID"))
ns = ENS.fromWeb3(w3)

print("lol.21xo.eth →", ns.address("lol.21xo.eth"))
print("tgr.21xo.eth →", ns.address("tgr.21xo.eth"))
print("xoseals.eth →", ns.address("xoseals.eth"))
