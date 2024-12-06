from flask import jsonify


def paginated_data(data, page, page_size):
    start = (page - 1) * page_size
    end = start + page_size
    pag_data = data[start:end]
    total_items = len(data)

    return jsonify({
        'data': pag_data,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_items + page_size - 1) // page_size
    })
