__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed


def parse_embed_from_table(table: list[tuple[str, str]]):
    if not table:
        raise Exception("Test result embed data table should contain at least one data row!")

    embed = Embed(title=table[0][0], description=table[0][1])

    for field in table[1:]:
        if field[0] == "!Footer!":
            embed.set_footer(text=field[1])
            break
        embed.add_field(name=field[0], value=field[1])

    return embed


def assert_same_embed_text(expected: Embed, actual: Embed):
    assert expected.title == expected.title
    assert expected.description == actual.description

    for expected_field, actual_field in zip(expected.fields, actual.fields):
        assert expected_field.name == actual_field.name
        assert expected_field.value == actual_field.value

    if expected.footer.text:
        assert expected.footer.text == actual.footer.text
