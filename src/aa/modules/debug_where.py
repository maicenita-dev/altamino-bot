from altamino import respObject

from src.aa import client
from src.utils import reply
from src.core.ctx import is_staff_ex, scope_of


@client.command(["!where"])
async def cmd_where(event: respObject.Event):
    a = event.message.author
    await reply(event, f"scope={scope_of(event)}\nrole={getattr(a, 'role', None)!r}\n"
                       f"staff={await is_staff_ex(event)}")
