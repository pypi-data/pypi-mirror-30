from flask import Flask, json, request, Response


def create_app(api, enable_cors=False):
    app = Flask(__name__)

    @app.route('/ping', methods=['GET'])
    def ping():
        return Response('pong', status=200)

    @app.route('/', methods=['OPTIONS'])
    def options():
        resp = Response('OK', status=200)
        if enable_cors:
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = '*'
        return resp

    @app.route('/', methods=['GET', 'POST'])
    def root():
        if request.headers.get('Content-Type', 'text/plain') != 'application/json':
            return Response('Error', status=200)
        api_request = request.json
        endpoint = api_request.get('endpoint', None)
        payload = api_request.get('payload', None)
        api_response = {'endpoint': endpoint}
        func = getattr(api, endpoint, None)
        if func:
            try:
                api_response['payload'] = func(**payload)
                api_response['success'] = True
            except Exception as e:
                api_response['error'] = str(e)
        else:
            api_response['error'] =  'Unknown endpoint: %s' % endpoint
        resp = Response(json.dumps(api_response), status=200, mimetype='application/json')
        if enable_cors:
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Headers'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = '*'
        return resp

    return app
