MAX_LEN = 1500


def _chunks(text: str, size: int = MAX_LEN) -> list:
    text = (text or "").strip()
    out = []
    while len(text) > size:
        cut = text.rfind("\n", 0, size)
        if cut < size // 2:
            cut = text.rfind(" ", 0, size)
        if cut < size // 2:
            cut = size
        out.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        out.append(text)
    return out


async def reply(event, text: str, **kwargs) -> None:
    """Responde en el chat donde llegó el comando (parte textos largos)."""
    tgt = getattr(event, "sub_client", None) or event.client
    for i, part in enumerate(_chunks(text)):
        await tgt.send_message(
            event.message.chatId, part, **(kwargs if i == 0 else {})
        )
