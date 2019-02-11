from flask import jsonify
# from flask import render_template
# from flask import flash
# from flask import current_app
# from flask import abort

from middleware import ztf_data
from middleware import dosthmsk


def init_api_routes(app):
    if app:
        app.add_url_rule('/', 'list_routes', list_routes,
                         methods=['GET'], defaults={'app': app})
        app.add_url_rule('/ztf', 'ztf', ztf_data, methods=['GET'])
        app.add_url_rule('/dosthmsk', 'dosthmsk', dosthmsk, methods=['GET'])


def list_routes(app):
    result = []
    for rt in app.url_map.iter_rules():
        result.append({
            'methods': list(rt.methods),
            'route': str(rt)
        })
    return jsonify({'routes': result, 'total': len(result)})
