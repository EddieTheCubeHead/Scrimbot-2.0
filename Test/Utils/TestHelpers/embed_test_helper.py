__version__ = "0.1"
__author__ = "Eetu Asikainen"

from behave.model import Table
from discord import Embed


def parse_embed_from_table(table: Table) -> Embed:
    if not table:
        raise Exception("Test result embed data table should contain at least one data row!")

    field_start = 1
    if table[0][0] == "Author" and table[1][0] == "Icon" and table[2][0] == "Colour":
        embed = Embed(title=table[3][0], description=table[3][1])
        embed.set_author(name=table[0][1], icon_url=table[1][1])
        embed.colour = int(table[2][1], 16)
        field_start = 4
    else:
        embed = Embed(title=table[0][0], description=table[0][1])

    for field in table[field_start:]:
        if field[0] == "Footer":
            embed.set_footer(text=field[1])
            break
        embed.add_field(name=field[0], value=field[1])

    return embed


def create_error_embed(error_message: str, command: str, help_portion: str = None) -> Embed:
    embed = Embed(title="ScrimBot Error", description=f"An error happened while processing command '{command}'")
    embed.add_field(name="Error message:", value=error_message)
    if help_portion:
        embed.add_field(name="To get help:", value=help_portion)
    embed.set_footer(text="If you think this behaviour is unintended, please report it in the bot repository in GitHub "
                          "at https://github.com/EddieTheCubeHead/Scrimbot-2.0")
    return embed


def pretty_print(expected, actual):
    string = "\n"
    string += f"{expected.author.name} | {actual.author.name}\n"
    string += f"{expected.author.icon_url} | {actual.author.icon_url}\n"
    string += f"{expected.colour} | {actual.colour}\n\n"
    string += f"{expected.title} | {actual.title}\n"
    string += f"{expected.description} | {actual.description}\n\n"
    for expected_field, actual_field in zip(expected.fields, actual.fields):
        string += f"{expected_field.name} | {actual_field.name}\n"
        string += f"{expected_field.value} | {actual_field.value}\n"
        string += f"{expected_field.inline} | {actual_field.inline}\n\n"
    string += f"{expected.footer.text} | {actual.footer.text}"
    return string


def assert_same_embed_text(expected: Embed, actual: Embed):
    assert expected.title == actual.title, f"{expected.title} != {actual.title}\n" \
                                           f"{pretty_print(expected, actual)}"
    assert expected.description == actual.description, f"{expected.description} != {actual.description}\n" \
                                                       f"{pretty_print(expected, actual)}"

    assert len(expected.fields) == len(actual.fields), \
        f"Expected {len(expected.fields)} fields, but got {len(actual.fields)}\n{pretty_print(expected, actual)}"
    for expected_field, actual_field in zip(expected.fields, actual.fields):
        assert expected_field.name == actual_field.name, f"{expected_field.name} != {actual_field.name}\n" \
                                                         f"{pretty_print(expected, actual)}"
        assert expected_field.value == actual_field.value, f"{expected_field.value} != {actual_field.value}\n" \
                                                           f"{pretty_print(expected, actual)}"

    if expected.footer.text:
        assert expected.footer.text == actual.footer.text, f"{expected.footer.text} != {actual.footer.text}\n" \
                                                           f"{pretty_print(expected, actual)}"
