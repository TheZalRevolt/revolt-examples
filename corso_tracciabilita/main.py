from algosdk.v2client import algod, indexer
from algosdk import transaction, account, logic, encoding
from algosdk.mnemonic import to_private_key
from contracts.contract import approval_program, clear_state_program
from utils import compile_program, create_app, wait_for_confirmation
from env_parameters import get_env
import base64

# * Prezzi soglia avranno sempre 3 cifre
ps_0 = b"033"
ps_1 = b"033"
ps_2 = b"033"
ps_3 = b"033"
ps_4 = b"033"
ps_5 = b"033"
ps_6 = b"033"
ps_7 = b"033"
ps_8 = b"033"
ps_9 = b"033"
ps_10 = b"033"
ps_11 = b"033"
ps_12 = b"033"
ps_13 = b"033"
ps_14 = b"033"
ps_15 = b"033"
ps_16 = b"033"
ps_17 = b"033"
ps_18 = b"033"
ps_19 = b"033"
ps_20 = b"033"
ps_21 = b"033"
ps_22 = b"033"
ps_23 = b"033"
ps_value = b"ps_"

for i in range(24):
    ps_value += eval(f"ps_{i}")

# * Funzioni generiche
def deploy_contract(algod_client, mnemonic_phrase):
    approval_program_compiled = compile_program(
        algod_client, approval_program())
    clear_program_compiled = compile_program(
        algod_client, clear_state_program())

    create_app(
        algod_client,
        to_private_key(mnemonic_phrase),
        approval_program_compiled,
        clear_program_compiled,
        create_global_schema(),
        create_local_schema(),
        [],
    )

def address_to_bytes(address: str) -> bytes:
    """
    Converte un indirizzo Algorand in bytes.
    
    :param address: L'indirizzo Algorand da convertire.
    :return: I bytes corrispondenti all'indirizzo.
    """
    return encoding.decode_address(address)

def bytes_to_address(address_bytes: bytes) -> str:
    """
    Converte bytes in un indirizzo Algorand.
    
    :param address_bytes: I bytes da convertire.
    :return: L'indirizzo Algorand corrispondente.
    """
    return encoding.encode_address(address_bytes)

def extract_ps_values(ps_value: str):
    """
    Estrae i valori per 'ps_' dalla stringa fornita.
    
    :param ps_value: La stringa contenente i valori.
    :return: Una lista con i valori estratti.
    """
    ps_values = []
    for i in range(0, len(ps_value), 3):
        ps_values.append(ps_value[i:i + 3])
    return ps_values

def extract_values(data_bytes: bytes):
    """
    Estrae i valori per 'balance_' e 'ps_' dalla stringa di byte fornita.
    
    :param dati_bytes: La stringa di byte contenente i dati.
    :return: Un dizionario con i valori estratti.
    """
    # Trova le posizioni delle sottostringhe di interesse
    ps_index = data_bytes.find(b"ps_")
    balance_index = data_bytes.find(b"balance_")
    
    # Estrai i valori
    ps_value = data_bytes[ps_index:balance_index] if ps_index != -1 and balance_index != -1 else None
    balance_value = data_bytes[balance_index:] if balance_index != -1 else None
    
    if ps_value:
        ps_value = ps_value.split(b"ps_")[1]  # Mantieni solo ciò che segue "ps_"
        ps_value = ps_value.decode('utf-8')
        ps_value = extract_ps_values(ps_value)
    
    if balance_value:
        balance_value = balance_value.split(b"balance_")[1] # Mantieni solo ciò che segue "balance_"
        balance_value = int.from_bytes(balance_value, 'big')

    return balance_value, ps_value

# * Funzioni per atm.py
def pay_transaction(algod_client, mnemonic_phrase, receiver_address, amount):
    sender_address = account.address_from_private_key(
        to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount,
    )

    return txn


def call_deposit(algod_client, mnemonic_phrase, app_id, amount, app_args):
    creator_address = account.address_from_private_key(
        to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=creator_address,
        sp=params,
        index=app_id,
        app_args=app_args,
    )

    application_address = logic.get_application_address(app_id)
    payment_txn = pay_transaction(
        algod_client, mnemonic_phrase, application_address, amount)
    transaction.assign_group_id([txn, payment_txn])

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    signed_payment_txn = payment_txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    transaction_response = algod_client.send_transactions(
        [signed_txn, signed_payment_txn])

    wait_for_confirmation(algod_client, tx_id)
    print("Txn hash:", transaction_response)


def call_withdraw(algod_client, mnemonic_phrase, app_id, app_args):
    user_address = account.address_from_private_key(
        to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=user_address,
        sp=params,
        index=app_id,
        app_args=app_args,
    )

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    transaction_response = algod_client.send_transactions([signed_txn])

    wait_for_confirmation(algod_client, tx_id)
    print("Txn hash:", transaction_response)


# * Funzioni per contract.py
def change_owner(algod_client, mnemonic_phrase, app_id, new_owner):
    sender = account.address_from_private_key(to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        app_args=[b"change_owner"],
        accounts=[new_owner]
    )

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)

def update_user(algod_client, mnemonic_phrase, app_id, user_id, user_value):
    sender = account.address_from_private_key(to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        app_args=[b"update_user", user_id, user_value],
    )

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)

def delete_user(algod_client, mnemonic_phrase, app_id, user_id):
    sender = account.address_from_private_key(to_private_key(mnemonic_phrase))
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=params,
        index=app_id,
        app_args=[b"delete_user", user_id],
    )

    signed_txn = txn.sign(to_private_key(mnemonic_phrase))
    tx_id = signed_txn.transaction.get_txid()

    algod_client.send_transactions([signed_txn])
    wait_for_confirmation(algod_client, tx_id)

def get_user_value(algod_indexer, app_id, user_id):
    app_info = algod_indexer.applications(app_id)
    app_global_state = app_info["params"]["global-state"]
    
    for state in app_global_state:
        key = base64.b64decode(state["key"]).decode('utf-8')
        
        if (key == "OWNER"):
            owner_address = bytes_to_address(base64.b64decode(state["value"]["bytes"]))
            print("Owner: ", owner_address)
            continue
        
        raw_value = state["value"]["bytes"]
        balance, ps_value = extract_values(base64.b64decode(raw_value))
        print("User ID: ", key)
        print("Balance: ", balance)
        print("PS Value: ", ps_value)

def main():
    env = get_env()

    algod_client = algod.AlgodClient(
        env.algod_token,
        env.algod_address,
    )
    algod_indexer = indexer.IndexerClient(
        env.algod_token,
        env.algod_address,
    )
    
    # * Dati per contract.py
    app_id = 722811038
    user_id = b"12"
    
    # deploy_contract(algod_client, env.mnemonic_phrase)
    
    # * Cambio del proprietario
    # new_owner = ""
    # change_owner(algod_client, env.mnemonic_phrase, app_id, new_owner)
    
    # * Creazione o aggiornamento di un utente
    user_balance = 9
    # User value: ps_value (stringa di numeri) + user_balance (intero a 8 byte)
    user_value = ps_value + b"balance_" + user_balance.to_bytes(8, "big")
    update_user(algod_client, env.mnemonic_phrase, app_id, user_id, user_value)
    
    # * Eliminazione di un utente
    # user_id = b"user_id"
    # delete_user(algod_client, env.mnemonic_phrase, app_id, user_id)
    
    # * Leggere il valore di un utente
    user_value = get_user_value(algod_indexer, app_id, user_id)
    # print("Stato: ", user_value)
    


def create_global_schema():
    # Il numero di interi e bytes globali dello smart contract
    # Le variabili globali non possono essere superiori a 64.
    # 25.000 microAlgos (0.025 Algos) per ogni variabile globale.
    # + 25.000 microAlgos per ogni variabile in bytes.
    # + 3.500 microAlgos per ogni variabile in int.
    global_ints = 0
    global_bytes = 25

    return transaction.StateSchema(global_ints, global_bytes)


def create_local_schema():
    # Il numero di interi e bytes locali dello smart contract
    # Le variabili locali non possono essere superiori a 16.
    # 25.000 microAlgos (0.025 Algos) per ogni variabile globale.
    # + 25.000 microAlgos per ogni variabile in bytes.
    # + 3.500 microAlgos per ogni variabile in int.
    local_ints = 0
    local_bytes = 0

    return transaction.StateSchema(local_ints, local_bytes)


if __name__ == "__main__":
    main()
