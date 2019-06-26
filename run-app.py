# -*- coding: utf-8 -*-

from app import app
import logging
from logging.handlers import RotatingFileHandler


if __name__ == '__main__':
    # initialize the log handler
    logHandler = RotatingFileHandler('info.log', maxBytes=100000, backupCount=1)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)
    # Running app in debug mode
    app.run(debug=True, host='0.0.0.0', port='5000')
