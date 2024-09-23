import os
import sys
from dotenv import load_dotenv

load_dotenv()

def get_env():
    """
    Prende le variabili d'ambiente (.env) e le restituisce in un oggetto Pydantic.
    """

    class Env:
        def __init__(self, mnemonic_phrase, algod_address, indexer_address, algod_token):
            self.mnemonic_phrase = mnemonic_phrase
            self.algod_address = algod_address
            self.indexer_address = indexer_address
            self.algod_token = algod_token
    
    env = None
    
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        env = Env(
            mnemonic_phrase=os.getenv("LOCAL_MNEMONIC_PHRASE"),
            algod_address=os.getenv("LOCAL_CLIENT_API_URL"),
            indexer_address=os.getenv("LOCAL_INDEXER_API_URL"),
            algod_token=os.getenv("LOCAL_CLIENT_TOKEN")
        )
    else:
        env = Env(
            mnemonic_phrase=os.getenv("MNEMONIC_PHRASE"),
            algod_address=os.getenv("CLIENT_API_URL"),
            indexer_address=os.getenv("INDEXER_API_URL"),
            algod_token=os.getenv("CLIENT_TOKEN")
        )

    return env