import base64
from algosdk import transaction
from algosdk import account


def compile_program(client, source_code):
    """
    Compila il codice sorgente TEAL e restituisce l'hash del contratto e il contratto formato in base64.

    Parameters:
        client (AlgodClient): Il client Algod per interagire con la blockchain Algorand.
        source_code (str): Il codice sorgente TEAL da compilare.

    Returns:
        bytes: Il contratto compilato in formato bytes.
    """

    # Compila il codice sorgente e restituisce l'hash del contratto e il contratto formato in base64
    compile_response = client.compile(source_code)

    return base64.b64decode(compile_response["result"])


def wait_for_confirmation(client, tx_id):
    """
    Funzione di utilità che attende la conferma di una transazione sulla blockchain.
    """
    last_round = client.status().get("last-round")
    tx_info = client.pending_transaction_info(tx_id)
    while not (tx_info.get("confirmed-round") and tx_info.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        tx_info = client.pending_transaction_info(tx_id)
    print(
        "Transaction {} confirmed in round {}.".format(
            tx_id, tx_info.get("confirmed-round")
        )
    )
    return tx_info


def create_app(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
    app_args,
):
    """
    Crea un nuovo smart contract (applicazione) sulla blockchain Algorand.

    Parameters:
        client (AlgodClient): Il client Algod per interagire con la blockchain Algorand.
        private_key (str): La chiave privata dell'account che crea il smart contract.
        approval_program (bytes): Il programma di approvazione del smart contract.
        clear_program (bytes): Il programma di clear state del smart contract.
        global_schema (dict): Lo schema globale del smart contract.
        local_schema (dict): Lo schema locale del smart contract.
        app_args (list): Gli argomenti del smart contract.

    Returns:
        int: L'ID del smart contract creato.
    """

    # Recupera l'indirizzo dell'account che creerà lo smart contract
    creator_address = account.address_from_private_key(private_key)

    """
    Modalità di completamento di una transazione senza alcuna modifica di stato
    OnComplete: indica come completare la transazione.
    NoOpOC: eseguire il contratto senza alterare lo stato globale.
    """
    on_complete = transaction.OnComplete.NoOpOC.real

    # Recupera i parametri consigliati per la transazione
    params = client.suggested_params()

    # Impostiamo il parametro flat_fee su True per pagare la tariffa fissa e non la tariffa in base al byte
    params.flat_fee = True
    # Tariffa fissa di 1000 microAlgos (0.001 Algos)
    params.fee = 1000

    txn = transaction.ApplicationCreateTxn(
        creator_address,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
    )

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    client.send_transactions([signed_txn])

    wait_for_confirmation(client, tx_id)

    transaction_response = client.pending_transaction_info(tx_id)

    app_id = transaction_response["application-index"]
    print("Created new app-id: ", app_id)

    return app_id
