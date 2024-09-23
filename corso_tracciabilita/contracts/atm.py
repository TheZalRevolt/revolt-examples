from pyteal import *

ACCOUNT_1 = Bytes("ACCOUNT_1")
ACCOUNT_1_BALANCE = Int(0)
ACCOUNT_2 = Bytes("ACCOUNT_2")
ACCOUNT_2_BALANCE = Int(0)

@Subroutine(TealType.uint64)
def deposit():
    account = Txn.application_args[0]
    amount = Gtxn[1].amount()
    
    old_balance = App.globalGet(account)
    new_balance = old_balance + amount
    
    return Seq(
        App.globalPut(account, new_balance),
        Return(Int(1)),
    )
    
@Subroutine(TealType.uint64)
def withdraw():
    return Seq(
        Return(Int(1)),
    )

def approval_program():
    on_creation = Seq(
        App.globalPut(ACCOUNT_1, ACCOUNT_1_BALANCE),
        App.globalPut(ACCOUNT_2, ACCOUNT_2_BALANCE),
        Return(Int(1)),
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.application_id() != Int(0), Return(deposit())]
    )
    return compileTeal(program, mode=Mode.Application, version=6)

def clear_state_program():
    program = Return(Int(0))
    return compileTeal(program, mode=Mode.Application, version=6)