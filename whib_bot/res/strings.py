bot_hello = """
Прывітанне! Я WHIB (Where Have I Been) бот. З маёй дапамогай ты можаш дадаць наведаныя месцы ў Беларусі і праверыць, у якіх раёнах ты пабываў ці яшчэ не быў.

Каб дадаць наведанае месца, у цябе ёсць некалькі опцый: 
        Напішы мне назву населенага пункта альбо
        Прымацуй лакацыю месца

Каб атрымаць карту наведаных табою месцаў - юзай каманду /visits_map_districts для раёнаў 
і /visits_map_regions для абласцей.

/unvisited_list верне табе спіс ненаведаных раёнаў.
/random_unvisited_district верне табе рандомны ненаведаны раён.
"""
bot_choose_option = 'Выберы патрэбнае месца са спісу ніжэй. Калі патрэбнага месца няма - пераправер запыт ці прымауй лакацыю.'
bot_place_not_found = 'Па запыце нічога не знойдзена :('
bot_generic_error = 'Штосьці пайшло не так :('
bot_server_error = 'Памылка сервера, паспрабуй крыху пазней яшчэ раз.'
bot_user_creation_error = 'Памылка ініцыялізацыі карыстача. Паспрабуй запусціць бота яшчэ раз.'
bot_discard_button = 'адмена'
bot_close_button = 'закрыць'
bot_empty_visits = 'У базе наведаных месцаў пуста'
bot_empty_unvisited_districts = 'Ненаведаных раёнаў не засталося!'
bot_unvisited_districts_list = 'Спіс яшчэ не наведаных раёнаў:'

def you_selected(place_name):
    return f'Выбрана {place_name}. Усё правільна?'

def selection_confirmed(place_name):
    return f'Візіт у {place_name} дададзены ў базу!'

def location_confirmed(lat, lon):
    return f'Лакацыя {lat} {lon} дададзена ў базу'