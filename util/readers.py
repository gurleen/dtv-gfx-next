"""
Socket message readers
"""


def handle_message(msg: dict) -> dict:
    """
    Attempt to handle message, return dict without handled pairs.
    """
    for key in msg.keys():
        value = msg[key]
        if key.startswith("casparcg:"):
            print("casparcg msg")
        else:
            continue
        msg.pop(key)
    return msg


def handle_casparcg(msg: dict):
    print(msg)