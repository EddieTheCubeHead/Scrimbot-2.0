__version__ = "0.1"
__author__ = "Eetu Asikainen"

import itertools

from behave.runner import Context
from discord import Embed

from Test.Utils.TestHelpers.id_parser import insert_ids


def parse_embed_from_table(context: Context) -> Embed:
    table = context.table
    if not table:
        raise Exception("Test result embed data table should contain at least one data row!")

    field_start = 1
    if table[0][0] == "Author" and table[1][0] == "Icon" and table[2][0] == "Colour":
        embed = _insert_author_info(context, table)
        field_start = 4
    else:
        embed = Embed(title=table[0][0], description=table[0][1])

    _create_fields(context, embed, field_start, table)

    return embed


def _insert_author_info(context, table):
    embed = Embed(title=table[3][0], description=insert_ids(context, table[3][1]))
    embed.set_author(name=table[0][1], icon_url=table[1][1])
    embed.colour = int(table[2][1], 16)
    return embed


def _create_fields(context, embed, field_start, table):
    for row in table[field_start:]:
        processed_field = _process_field(row, context)
        if processed_field[0] == "Footer":
            embed.set_footer(text=processed_field[1])
            break
        embed.add_field(name=processed_field[0], value=processed_field[1])


def _process_field(field, context) -> list[str]:
    fields = []
    for part in field:
        processed = insert_ids(context, part)
        fields.append(processed)
    return fields


def create_error_embed(error_message: str, command: str, context: Context, help_portion: str = None) -> Embed:
    embed = Embed(title="ScrimBot Error", description=f"An error happened while processing command '{command}'")
    embed.add_field(name="Error message:", value=insert_ids(context, error_message))
    if help_portion:
        embed.add_field(name="To get help:", value=help_portion)
    embed.set_footer(text="If you think this behaviour is unintended, please report it in the bot repository in GitHub "
                          "at https://github.com/EddieTheCubeHead/Scrimbot-2.0")
    return embed


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


class EmptyField:
    name = None
    value = None
    inline = None


def pretty_print(expected, actual):
    string = "\n"
    string += f"{expected.author.name} | {actual.author.name}\n"
    string += f"{expected.author.icon_url} | {actual.author.icon_url}\n"
    string += f"{expected.colour} | {actual.colour}\n\n"
    string += f"{expected.title} | {actual.title}\n"
    string += f"{expected.description} | {actual.description}\n\n"
    for expected_field, actual_field in itertools.zip_longest(expected.fields, actual.fields, fillvalue=EmptyField):
        string += f"{expected_field.name} | {actual_field.name}\n"
        string += f"{expected_field.value} | {actual_field.value}\n"
        string += f"{expected_field.inline} | {actual_field.inline}\n\n"
    string += f"{expected.footer.text} | {actual.footer.text}"
    return string
