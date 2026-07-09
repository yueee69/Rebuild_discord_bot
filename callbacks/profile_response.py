import nextcord
from nextcord import Interaction


async def send_profile_components(
    interaction: Interaction,
    components: list[tuple],
    *,
    delete_source_message: bool = False,
):
    if not components:
        return

    first_embed, first_view, first_ephemeral, first_content = components[0]
    if first_ephemeral:
        await _send_interaction_message(
            interaction,
            first_embed,
            first_view,
            first_ephemeral,
            first_content,
        )
        await _send_followups(interaction, components[1:])
        return

    if not interaction.response.is_done():
        await interaction.response.defer()

    if delete_source_message:
        await _delete_source_message(interaction)

    await _send_followup_message(interaction, first_embed, first_view, first_content)
    await _send_followups(interaction, components[1:])


async def _send_interaction_message(
    interaction: Interaction,
    embed,
    view,
    ephemeral: bool,
    content,
):
    if interaction.response.is_done():
        await interaction.followup.send(
            ephemeral=ephemeral,
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {}),
        )
        return

    await interaction.response.send_message(
        ephemeral=ephemeral,
        **({"embed": embed} if embed else {}),
        **({"view": view} if view else {}),
        **({"content": content} if content else {}),
    )


async def _send_followup_message(interaction: Interaction, embed, view, content):
    await interaction.followup.send(
        **({"embed": embed} if embed else {}),
        **({"view": view} if view else {}),
        **({"content": content} if content else {}),
    )


async def _send_followups(interaction: Interaction, components: list[tuple]):
    for embed, view, ephemeral, content in components:
        if ephemeral:
            await interaction.followup.send(
                ephemeral=True,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {}),
            )
        else:
            await _send_followup_message(interaction, embed, view, content)


async def _delete_source_message(interaction: Interaction):
    message = getattr(interaction, "message", None)
    if not message:
        return

    try:
        await message.delete()
    except (nextcord.NotFound, nextcord.Forbidden, nextcord.HTTPException):
        return
