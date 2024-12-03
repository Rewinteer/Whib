# Map-related
visited = 'быў'
not_visited = 'яшчэ не паспеў'
district_note = '(гарады абласнога падпарадкавання лічацца асобна)'
region_note = '(Мінск лічыцца асобна)'
bot_link = '@whibBY_bot'
map_name = 'visited_map.png'

# bot-related
bot_hello = """
Прывітанне! Я WHIB (Where Have I Been) бот. З маёй дапамогай ты можаш дадаць наведаныя месцы ў Беларусі і праверыць, у якіх раёнах ты пабываў ці яшчэ не быў.

Каб дадаць наведанае месца, у цябе ёсць некалькі опцый: 
        Напішы мне назву населенага пункта альбо
        Прымацуй лакацыю месца
        
Каб атрымаць карту наведаных табою месцаў - юзай каманду /visits_map_districts для раёнаў 
і /visits_map_regions для абласцей.
"""
bot_choose_option = 'Выберы патрэбнае месца са спісу ніжэй. Калі патрэбнага месца няма - пераправер запыт ці прымауй лакацыю.'
bot_place_not_found = 'Па запыце нічога не знойдзена :('
bot_generic_error = 'Штосьці пайшло не так :('
bot_server_error = 'Памылка сервера, паспрабуй крыху пазней яшчэ раз'
bot_user_creation_error = 'Памылка ініцыялізацыі карыстача. Паспрабуй запусціць бота яшчэ раз'
bot_discard_button = 'адмена'
bot_empty_visits = 'У базе наведаных месцаў пуста'


def visited_districts(visited, total):
    return f'Наведана {visited}/{total} раёнаў!'


def visited_regions(visited, total):
    return f'Наведана {visited}/{total} абласцей!'


def you_selected(place_name):
    return f'Выбрана {place_name}. Усё правільна?'

def selection_confirmed(place_name):
    return f'Візіт у {place_name} дададзены ў базу!'