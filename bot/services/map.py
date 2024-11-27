from matplotlib.patches import Patch

import bot.database.db_utils as db_utils
import bot.strings as strings
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tempfile


def get_visited_map(tg_chat_id: int, class_name: str):
    visited_list = db_utils.get_visited(tg_chat_id, class_name)
    df = pd.DataFrame.from_records(visited_list, columns=['name', 'is_visited', 'geometry'])
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])

    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf['color'] = gdf['is_visited'].map({True: '#3182bd', False: '#deebf7'})

    visited = gdf['is_visited'].sum()
    total_rows = len(gdf)
    districts = total_rows > 7
    fig_note = strings.visited_districts(visited, total_rows) if districts else strings.visited_regions(visited, total_rows)

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

    # bot link
    fig.text(0.2, 0.1, strings.bot_link, fontsize=10, ha='left', va='bottom')

    plt.savefig('visited_map.png', dpi=150, bbox_inches='tight')

if __name__ == '__main__':
    get_visited_map(234, 'District')