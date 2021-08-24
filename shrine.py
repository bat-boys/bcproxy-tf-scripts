from tf import eval as tfeval  # type: ignore
from typing import Sequence

from tfutils import tfprint

MESSAGES: Sequence[str] = [
    "You feel that your prayers are ignored.",
    "You feel like you have offended the gods somehow.",
    "You hear the rumble of distant thunder.",
    "You sense a feeling of mild discontent.",
    "Clouds part and a ray of light shines down on the altar.",
    "You feel relaxed.",
    "A warm feeling spreads around your body.",
    "A weary voice echoes in your mind 'Nice to see.. an old friend.'",
    "You raise your eyes to the sky as celestial wind flows through you.",
    "You burst out in tears as feeling of sudden happiness overwhelms you.",
]


def setup():
    for i, msg in enumerate(MESSAGES):
        tfeval(
            "/def -i -F -p10 -msimple -t`{1}` shrine_message_{0}".format(i, msg)
            + " = /substitute \%* ({0}/{1})".format(i, len(MESSAGES) - 1)
        )

    tfprint("Loaded shrine.py")


setup()
