Copyright (c) 2018 Beto Dealmeida

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: console_log
        ===========
        
        This module provides a WSGI middleware that allows you to log to the
        browser console from Python:
        
        .. code::
        
            import logging
        
            from flask import Flask
        
            from console_log import ConsoleLog
        
            console = logging.getLogger('console')
            console.setLevel(logging.DEBUG)
        
            app = Flask(__name__)
        
            @app.route('/')
            def hello():
                logger.error('Error logged from Python')
                logger.warning('Warning logged from Python')
                logger.info('Info logged from Python')
                logger.debug('Debug logged from Python')
                logger.debug({'foo': ['bar', 'baz']})
                return "Hello World!"
        
            app.wsgi_app = ConsoleLog(app.wsgi_app, console)
        
        The logged messages will then show up in the browser console.
        
        
        How it works
        ============
        
        The new WSGI app does two things:
        
        1. Creates a websocket backchannel.
        2. Injects Javascript code into HTML responses, fetching data from the
           websocket channel and logging them to console.
        
Platform: UNKNOWN
Classifier: License :: OSI Approved :: MIT License
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Programming Language :: Python :: 3.5
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Provides-Extra: dev
Provides-Extra: examples
