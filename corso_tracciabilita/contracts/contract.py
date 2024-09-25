from pyteal import *

OWNER = Bytes("OWNER")

@Subroutine(TealType.uint64)
def update_user():
    user_id = Txn.application_args[1]
    user_value = Txn.application_args[2]
    sender = Txn.sender() # Txn.accounts[0] Sono la stessa cosa
    
    return Seq(
        Assert(sender == App.globalGet(OWNER)),
        App.globalPut(user_id, user_value),
        Return(Int(1)),
    )

@Subroutine(TealType.uint64)
def change_owner():
    new_owner = Txn.accounts[1] # Nella posizione 0 c'è chi ha chiamato il contratto
    
    sender = Txn.sender()
    
    return Seq(
        Assert(sender == App.globalGet(OWNER)),
        App.globalPut(OWNER, new_owner),
        Return(Int(1)),
    )

@Subroutine(TealType.uint64)
def delete_user():
    user_id = Txn.application_args[1]
    sender = Txn.sender()
    
    return Seq(
        Assert(sender == App.globalGet(OWNER)),
        App.globalDel(user_id),
        Return(Int(1)),
    )

def approval_program():
    # Condizioni iniziali
    on_creation = Seq(
        App.globalPut(OWNER, Txn.sender()),
        Return(Int(1)),
    )
    
    on_handle = Cond(
        [Txn.application_args[0] == Bytes("update_user"), Return(update_user())],
        [Txn.application_args[0] == Bytes("change_owner"), Return(change_owner())],
        [Txn.application_args[0] == Bytes("delete_user"), Return(delete_user())],
    )
    
    # Gestione delle chiamate del contratto
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.NoOp, on_handle],
    )

    return compileTeal(program, mode=Mode.Application, version=6)

def clear_state_program():
    program = Return(Int(0))
    return compileTeal(program, mode=Mode.Application, version=6)


def compile_contract():
    """
    Compila i programmi di approvazione e di clear state del contratto.
    Salva i programmi compilati nei file "approva.teal" e "clear.teal", nella cartella "compiled_contracts".
    """

    approval = approval_program()
    approval_file = open("compiled_contracts/approval.teal", "w")
    approval_file.write(approval)

    clear = clear_state_program()
    clear_file = open("compiled_contracts/clear.teal", "w")
    clear_file.write(clear)

    return approval, clear


if __name__ == "__main__":
    approval, clear = compile_contract()

    print("Approval program:")
    print(approval)

    print("\nClear state program:")
    print(clear)
