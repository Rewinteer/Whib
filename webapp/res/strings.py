visited = 'быў'
not_visited = 'яшчэ не паспеў'
district_note = '(гарады абласнога падпарадкавання лічацца асобна)'
region_note = '(Мінск лічыцца асобна)'
bot_link = '@whibBY_bot'
map_name = 'visited_map.png'


def visited_districts(visited, total):
    return f'Наведана {visited}/{total} раёнаў!'


def visited_regions(visited, total):
    return f'Наведана {visited}/{total} абласцей!'
