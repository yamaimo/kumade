# Kumadefile for test

import kumade as ku

ku.set_default("greet")


@ku.task("greet")
@ku.help("Greet all.")
def greeting() -> None:
    print("Hi, this is Kumade.")
