import os.path

from matplotlib.patches import Patch

import bot.database.db_utils as db_utils
import bot.strings as strings
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from bot.logging_config import logger

from bot.database.models import District

map_path = 'services/tmp/'


def is_map_exists(path):
    return os.path.isfile(path)


def remove_generated_maps(tg_chat_id):
    try:
        removed_count = 0
        for file_name in os.listdir(map_path):
            file_path = os.path.join(map_path, file_name)
            if os.path.isfile(file_path) and file_name.startswith(f'{tg_chat_id}:'):
                os.remove(file_path)
                removed_count += 1
                logger.info(f'removed {file_path}')

            if removed_count == 2:
                break
    except Exception as e:
        logger.error(f'failed to remove map files for tg_chat_id {tg_chat_id} - {e}')


def get_visited_map(tg_chat_id: int, unit_flag: str):
    filename = f'{tg_chat_id}:{unit_flag}s:{strings.map_name}'
    path = map_path + filename
    if is_map_exists(path):
        logger.info(f'got {path} map from the server without recreation')
        return path

    visited_list = db_utils.get_visited(tg_chat_id=tg_chat_id, unit_flag=unit_flag)
    if not visited_list:
        logger.info(f'visited list for tg_chat_id {tg_chat_id} is empty')
        return None

    df = pd.DataFrame.from_records(visited_list, columns=['name', 'is_visited', 'geometry'])
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])

    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf['color'] = gdf['is_visited'].map({True: '#3182bd', False: '#deebf7'})

    visited = gdf['is_visited'].sum()
    total_rows = len(gdf)
    districts = unit_flag == District.__name__
    fig_note = strings.visited_districts(visited, total_rows) if districts else strings.visited_regions(visited,
                                                                                                        total_rows)

    fig, ax = plt.subplots()
    gdf.plot(
        ax=ax,
        aspect=1.6,
        color=gdf['color'],
        edgecolor='gray',
        linewidth=0.5
    )

    ax.axis('off')
    legend_elements = [
        Patch(facecolor='#3182bd', edgecolor='gray', label=strings.visited),
        Patch(facecolor='#deebf7', edgecolor='gray', label=strings.not_visited)
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    # Header
    fig.text(0.5, 0.95, fig_note, fontsize=12, ha='center', va='top')
    if districts:
        fig.text(0.5, 0.9, strings.district_note, fontsize=8, ha='center', va='top')
    else:
        fig.text(0.5, 0.9, strings.region_note, fontsize=8, ha='center', va='top')

    # bot link
    fig.text(0.2, 0.1, strings.bot_link, fontsize=10, ha='left', va='bottom')

    plt.savefig(f'{path}', dpi=150, bbox_inches='tight')
    logger.info(f'created a map file {filename}')
    return path


if __name__ == '__main__':
    get_visited_map(456, 'District')
