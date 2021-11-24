__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed


def parse_embed_from_table(table: list[tuple[str, str]]) -> Embed:
    if not table:
        raise Exception("Test result embed data table should contain at least one data row!")

    embed = Embed(title=table[0][0], description=table[0][1])

    for field in table[1:]:
        if field[0] == "Footer":
            embed.set_footer(text=field[1])
            break
        embed.add_field(name=field[0], value=field[1])

    return embed


def create_error_embed(error_message: str) -> Embed:
    embed = Embed(title="ScrimBot: Error", description="An error happened while processing command 'register'")
    embed.add_field(name="Error message:", value=error_message)
    embed.set_footer(text="If you think this behaviour is unintended, please report it in the bot repository in GitHub "
                          "at https://github.com/EddieTheCubeHead/Scrimbot-2.0")


def assert_same_embed_text(expected: Embed, actual: Embed):
    assert expected.title == actual.title, f"{expected.title} != {actual.title}"
    assert expected.description == actual.description, f"{expected.description} != {actual.description}"

    assert len(expected.fields) == len(actual.fields), \
        f"Expected {len(expected.fields)} fields, but got {len(actual.fields)}"
    for expected_field, actual_field in zip(expected.fields, actual.fields):
        assert expected_field.name == actual_field.name, f"{expected_field.name} != {actual_field.name}"
        assert expected_field.value == actual_field.value, f"{expected_field.value} != {actual_field.value}"

    if expected.footer.text:
        assert expected.footer.text == actual.footer.text, f"{expected.footer.text} != {actual.footer.text}"
