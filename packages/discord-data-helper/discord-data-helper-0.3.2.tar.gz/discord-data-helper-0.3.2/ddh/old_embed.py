import discord

def simplembed(color = 0x000000, title = None, description = None, url = None, footer = None, image = None, thumbnail = None, author = None, field = None):
    """
    Makes discord embed to very simple

    Attributes
    -----------
    color: :class:`int` or :class:`Colour`
        The color of the embed.
    title: :class:`str`
        The title of the embed.
    description: :class:`str`
        The description of the embed.
    url: :class:`str`
        The URL of the embed.
    footer: :class:`list` or :class:`dict`
        The footer of the embed.
        If the footer is list, The first content will be the name and the second content will be the icon_url.
        If the footer is dict, Name content will be the name and icon_url content will be the icon_url.
        And icon_url is only HTTP(S) is supported.
    image: :class:`str`
        The image's url of the embed, Only HTTP(S) is supported.
    thumbnail: :class:`str`
        The thumbnail's url of the embed, Only HTTP(S) is supported.
    author: :class:`list` or :class:`dict`
        The author of the embed.
        If the author is list, The first content will be the name, The second content will be the url and the third content will be the icon_url.
        If the author is dict, Name content will be the name, url content will be the url and icon_url content will be the icon_url.
        And icon_url is only HTTP(S) is supported.
    field: :class:`dict`
        The field(s) of the embed.
        The name is the first element(s), The value is value and if you wanna to enable inline mode, just add inline element and set to True.
        ex)

        .. code-block:: python3

            {"This will be the name":{"value":"This will be the value", "inline":True}} #inline is not require

    :returns discord.Embed: Enjoy :)
    """
    if not type(color) is int and not color is discord.colour.Colour:
        raise TypeError('The color must be a int, or discord.Colour.')
    if not type(title) is str and not title is None:
        raise TypeError('The title must be a str, or None.')
    if not type(description) is str and not description is None:
        raise TypeError('The description must be a str, or None.')
    if not type(url) is str and not url is None:
        raise TypeError('The url must be a str, or None.')
    embed = discord.Embed(color = color, title = title, description = description, url = url)
    if footer is None:
        pass
    elif type(footer) is dict:
        if footer.__contains__('name'):
            f_name = str(footer['name'])
        else:
            f_name = None
        if footer.__contains__('icon_url'):
            f_icon = str(footer['icon_url'])
        else:
            f_icon = None
        embed.set_footer(name = f_name, icon_url = f_icon)
    elif type(footer) is list:
        try:
            f_name = str(footer[0])
        except IndexError:
            f_name = None
        try:
            f_icon = str(footer[1])
        except IndexError:
            f_icon = None
        embed.set_footer(name = f_name, icon_url = f_icon)
    else:
        raise TypeError('The footer must be a dict, list, or None.')
    if image is None:
        pass
    elif type(image) is str:
        embed.set_image(url = image)
    else:
        raise TypeError('The image must be a str, or None.')
    if thumbnail is None:
        pass
    elif type(thumbnail) is str:
        embed.set_thumbnail(url = thumbnail)
    else:
        raise TypeError('The thumbnail must be a str, or None.')
    if author is None:
        pass
    elif type(author) is list:
        try:
            a_name = author[0]
        except IndexError:
            a_name = None
        try:
            a_url = author[1]
        except IndexError:
            a_url = None
        try:
            a_icon = author[2]
        except IndexError:
            a_icon = None
        embed.set_author(name = a_name, url = a_url, icon_url = a_icon)
    elif type(author) is dict:
        if author.__contains__('name'):
            a_name = author['name']
        else:
            a_name = None
        if author.__contains__('url'):
            a_url = author['url']
        else:
            a_url = None
        if author.__contains__('icon_url'):
            a_icon = author['icon_url']
        else:
            a_icon = None
        embed.set_author(name = a_name, url = a_url, icon_url = a_icon)
    else:
        raise TypeError('The author must be a list, dict, or None.')
    if field is None:
        pass
    elif type(field) is dict:
        for a, b in field.items():
            name = a
            for n, v in b.items():
                if n == 'value':
                    value = str(v)
                if n == 'inline':
                    if not v is bool:
                        raise TypeError('The inline in field must be a bool.')
                    inline = v
            try:
                embed.add_field(name = name, value = value, inline = inline)
            except NameError:
                embed.add_field(name = name, value = value)

    return embed
