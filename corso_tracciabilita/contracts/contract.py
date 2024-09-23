from pyteal import *

# Definiamo le stazioni di consegna
STATIONS = ["stazione1", "stazione2", "stazione3", "stazione4"]
ALGO = Int(1_000_000)
# Definiamo le chiavi di stato
CURRENT_STATION_KEY = Bytes("cur_station")
COURIER_ID_KEY = Bytes("courier_id")
TOTAL_TRIPS_KEY = Bytes("total_trips")


def approval_program():
    # Parametri del contratto
    courier_id = Txn.application_args[0]
    station = Txn.application_args[1]
    action = Txn.application_args[2]  # "arrivo" o "partenza"

    # Condizioni iniziali
    on_creation = Seq(
        App.globalPut(COURIER_ID_KEY, courier_id),
        App.globalPut(CURRENT_STATION_KEY, Bytes("")),
        App.globalPut(TOTAL_TRIPS_KEY, Int(0)),
        Return(Int(1)),
    )

    # Arrivo del corriere in una stazione
    on_arrival = Seq(
        [
            Assert(action == Bytes("arrivo")),
            App.globalPut(CURRENT_STATION_KEY, station),
            Return(Int(1)),
        ]
    )

    # Partenza del corriere da una stazione
    on_departure = Seq(
        [
            Assert(action == Bytes("partenza")),
            If(
                App.globalGet(CURRENT_STATION_KEY) == station,
                Seq(
                    [
                        # Controllo se è l'ultima stazione
                        If(
                            station == Bytes(STATIONS[-1]),
                            Seq(
                                [
                                    App.globalPut(
                                        CURRENT_STATION_KEY, Bytes("")),
                                    App.globalPut(
                                        TOTAL_TRIPS_KEY,
                                        App.globalGet(
                                            TOTAL_TRIPS_KEY) + Int(1),
                                    ),
                                ]
                            ),
                            # Non è l'ultima stazione, quindi resetto solo la stazione corrente
                            App.globalPut(CURRENT_STATION_KEY, Bytes("")),
                        )
                    ]
                ),
                Reject(),
            ),
            Return(Int(1)),
        ]
    )

    # Gestione delle chiamate del contratto
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [
            Txn.application_id() != Int(0),
            Cond(
                [action == Bytes("arrivo"), on_arrival],
                [action == Bytes("partenza"), on_departure],
            ),
        ],
    )

    return compileTeal(program, mode=Mode.Application, version=6)


def clear_state_program():
    program = Return(Int(1))
    return compileTeal(program, mode=Mode.Application, version=6)


def compile_contract():
    """
    Compila i programmi di approvazione e di clear state del contratto.
    Salva i programmi compilati nei file "approva.teal" e "clear.teal", nella cartella "compiled_contracts".
    """

    approval = approval_program()
    approval_file = open("compiled_contracts/approva.teal", "w")
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
