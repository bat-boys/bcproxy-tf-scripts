from tf import eval as tfeval  # type: ignore
from typing import Sequence

from tfutils import tfprint

CHARGES: Sequence[str] = [
    "shedding an eerie green light.",
    "shedding an eerie yellow light.",
    "shedding an eerie cyan light.",
    "shedding an eerie blue light.",
    "shedding an eerie magenta light.",
    "shedding an eerie red light.",
    "shedding an eerie bright green light.",
    "shedding an eerie bright yellow light.",
    "shedding an eerie bright cyan light.",
    "shedding an eerie bright blue light.",
    "shedding an eerie bright magenta light.",
    "shedding an eerie bright red light.",
]


def setup():

    for i, msg in enumerate(CHARGES):
        tfeval(
            "/def -i -F -p10 -msimple -t`{1}` druid_staff_charge_{0}".format(i, msg)
            + " = /substitute \%* ({0}/{1})".format(i, len(CHARGES) - 1)
        )

    tfeval(
        "/def -i -F -ag -p10 -msimple "
        + "-t`spec_spell: You sense power flowing into your Staff of Druids.` "
        + "druid_charge_staff_done = @ch spr;sensecharge staff"
    )

    tfprint("Loaded druid.py")


setup()
