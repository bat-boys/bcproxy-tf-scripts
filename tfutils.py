from tf import eval  # type: ignore


def tfprint(s: str):
    for line in s.split("\n"):
        eval("/echo -p @{Crgb450}»@{n} " + line + "@{n}")
