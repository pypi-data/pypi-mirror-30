import discord

def simplembed(_embed):
    if not type(_embed) is dict:
        raise TypeError('The embed must be a dict.')
    color = _embed['color']
    title = _embed.get('title')
    description = _embed.get('description')
    url = _embed.get('url')
    embed = discord.Embed(color = color, title = title, description = description, url = url)
    footer = _embed.get('footer')
    if footer is None:
        pass
    else:
        f_name = _embed.get('f_name')
        f_icon = _embed.get('f_icon')
        embed.set_footer(name = f_name, icon_url = f_icon)
    image = _embed.get('image')
    if not image is None:
        embed.set_image(url = image)
    thumbnail = _embed.get('thumbnail')
    if not thumbnail is None:
        embed.set_thumbnail(url = thumbnail)
    author = _embed.get('author')
    if not author is None:
        a_name = author.get('name')
        a_url = author.get('url')
        a_icon = author.get('icon')
        embed.set_author(name = a_name, url = a_url, icon_url = a_icon)
    field = _embed.get('field')
    if not field is None:
        has_inline = False
        for a, b in field.items():
            name = a
            for n, v in b.items():
                if n == 'value':
                    value = str(v)
                if n == 'inline':
                    if v is bool:
                        inline = v
                        has_inline = True
                    else:
                        raise TypeError('The inline must me a bool.')
            embed.add_field(name = name, value = value, inline = inline) if has_inline else embed.add_field(name = name, value = value)
    return embed