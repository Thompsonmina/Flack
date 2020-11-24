web: gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker --log-file=- application:app

web: ygunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --log-file=- application:app