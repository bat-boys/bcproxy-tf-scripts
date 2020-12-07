from tf import eval as tfeval  # type: ignore
from typing import Sequence

from tfutils import tfprint

AURAS: Sequence[str] = [
    "You feel nothing. Your drained energy supply is empty.",
    "You feel a slight tinge only. Your drained energy supply is low.",
    "You feel a mild tingle. You have a fair amount of drained energy left.",
    "You feel a soothing inner warmth. You have a good supply of drained energy.",
    "You feel a rushing sensation within your soul. You have a strong surplus of drained energy.",
    "You feel a torrent of energy rushing through your body!",
    "You are a towering inferno of energy! Your supply is at full strength!",
]


def setup():

    for i, msg in enumerate(AURAS):
        tfeval(
            "/def -i -F -p10 -msimple -t`{1}` channeller_supply_{0}".format(i, msg)
            + " = /substitute \%* ({0}/{1})".format(i, len(AURAS) - 1)
        )

    tfeval(
        "/def -i -F -ag -p10 -msimple "
        + "-t`You take a deep breath and close your eyes.` "
        + "channeller_gag_supply_start"
    )

    tfprint("Loaded channeller.py")


setup()
