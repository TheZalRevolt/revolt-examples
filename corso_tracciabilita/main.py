from algosdk.v2client import algod
from algosdk import transaction, account, logic
from algosdk.mnemonic import to_private_key
from contracts.atm import approval_program, clear_state_program
from utils import compile_program, create_app, wait_for_confirmation
from env_parameters import get_env


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


def main():
    env = get_env()

    algod_client = algod.AlgodClient(
        env.algod_token,
        env.algod_address,
    )

    app_id = 722627808
    # deploy_contract(algod_client, env.mnemonic_phrase)

    call_deposit(algod_client, env.mnemonic_phrase,
                 app_id, 1500, ["deposit", "ACCOUNT_1"])

    call_withdraw(algod_client, env.mnemonic_phrase,
                  app_id, ["withdraw", "ACCOUNT_1", 1000])


def create_global_schema():
    # Il numero di interi e bytes globali dello smart contract
    # Le variabili globali non possono essere superiori a 64.
    # 25.000 microAlgos (0.025 Algos) per ogni variabile globale.
    # + 25.000 microAlgos per ogni variabile in bytes.
    # + 3.500 microAlgos per ogni variabile in int.
    global_ints = 2
    global_bytes = 0

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
