Flask-Dropzone
================
Upload file in Flask with [Dropzone.js](http://www.dropzonejs.com/).

[中文文档](http://greyli.com/flask-dropzone-add-file-upload-capabilities-for-your-project/)

Installation
------------
```
$ pip install flask-dropzone
```

Quick Start
-----------

Step 1: Initialize the extension:

```python
from flask_dropzone import Dropzone
    
dropzone = Dropzone(app)
```
This extension also supports the [Flask application factory pattern](http://flask.pocoo.org/docs/latest/patterns/appfactories/) by allowing you to create a Dropzone object and then separately initialize it for an app:

```python
dropzone = Dropzone()

def create_app(config):
    app = Flask(__name__)
    ...
    dropzone.init_app(app)
    ...
    return app
```

Step 2: In your `<head>` section of your template add the following code:

```jinja    
{{ dropzone.load() }}
```

You can assign the version of Dropzone.js through `version` argument, the default value is `5.2.0`.

Step 3: Creating a Drop Zone with `create()`:

```jinja 
{{ dropzone.create(action_view='your_upload_view') }}
```

Also remember to edit the action view to your view endpoint (usually the name of view function) that handles
the uploads.

Beautify Dropzone
-----------------

Style it according to your preferences through `style()` method:

```jinja
{{ dropzone.style('border: 2px dashed #0087F7; margin: 10%; min-height: 400px;') }}
```

Configuration 
-------------

The supported list of config options is shown below:

| Name                     | Default Value | Info |
| ------------------------ | ------------- | ---- |
| `DROPZONE_SERVE_LOCAL`   | `False`       | default to retrieve `dropzone.js` from CDN |
| `DROPZONE_MAX_FILE_SIZE` | 3             | max allowed file size. unit: MB   |
| `DROPZONE_INPUT_NAME`    | `file`        | the `name` attr in <input>: `<input type="file" name="file">` |
| `DROPZONE_ALLOWED_FILE_CUSTOM` | `False` | see detail below |
| `DROPZONE_ALLOWED_FILE_TYPE` | `'default'` | see detail below |
| `DROPZONE_MAX_FILES` | 'null' | the max files user can upload once |
| `DROPZONE_DEFAULT_MESSAGE` | "Drop files here to upload" | message displayed on drop area |
| `DROPZONE_INVALID_FILE_TYPE` |  "You can't upload files of this type." | error message |
| `DROPZONE_FILE_TOO_BIG` | "File is too big {{filesize}}. Max filesize: {{maxFilesize}}MiB." | error message |
| `DROPZONE_SERVER_ERROR` | "Server error: {{statusCode}}" | error message |
| `DROPZONE_BROWSER_UNSUPPORTED` | "Your browser does not support drag'n'drop file uploads." | error message | 
| `DROPZONE_MAX_FILE_EXCEED` | "Your can't upload any more files." | error message |
| `DROPZONE_UPLOAD_MULTIPLE` | `False` | whether to send multiple files in one request. |
| `DROPZONE_PARALLEL_UPLOADS` | 2 | how many uploads will handled in per request when `DROPZONE_UPLOAD_MULTIPLE` set to True. |
| `DROPZONE_REDIRECT_VIEW` | `None` | the view to redierct when upload was completed. |
| `DROPZONE_ENABLE_CSRF` | `False` | enable CSRF protect, see detail below |

You can use these file type: 
```python
allowed_file_type = {
    'default': 'image/*, audio/*, video/*, text/*, application/*',
    'image': 'image/*',
    'audio': 'audio/*',
    'video': 'video/*',
    'text': 'text/*',
    'app': 'application/*'
    }
```
If you want to set the allowed file type by yourself, you need to set 
`DROPZONE_ALLOWED_FILE_CUSTOM` to `True`, then add mime type or file extensions to
`DROPZONE_ALLOWED_FILE_TYPE`, such as:
```python
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*, .pdf, .txt'
```

Consult the [dropzone.js documentation](http://dropzonejs.com/) for details on these options.


Save uploads with Flask
-----------------------

```python
import os

from flask import Flask, request
from flask_dropzone import Dropzone

app = Flask(__name__)

dropzone = Dropzone(app)

@app.route('/uploads', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(the_path_to_save, f.filename))

    return 'upload template'
```

See `examples/basic` for more detail.

Parallel Uploads
----------------

If you set `DROPZONE_UPLOAD_MULTIPLE` as True, then you need to save multiple uploads in 
single request. 

However, you can't get a list of file with `request.files.getlist('file')`. When you 
enable parallel upload, Dropzone.js will append a index number after each files, for example:
`file[2]`, `file[1]`, `file[0]`. So, you have to save files like this:
```python
    for key, f in request.files.iteritems():
        if key.startswith('file'):
            f.save(os.path.join(the_path_to_save, f.filename)) 
```
Here is the full example:
```python
...
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True  # enable parallel upload
app.config['DROPZONE_PARALLEL_UPLOADS'] = 3  # handle 3 file per request

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        for key, f in request.files.iteritems():  # use request.files.items() in Python3
            if key.startswith('file'):
                f.save(os.path.join(the_path_to_save, f.filename))

    return 'upload template'
```

See `examples/parallel-upload` for more detail.

CSRF Protect
------------

The CSRF Protect feature was provided by Flask-WTF's `CSRFProtect` extension, so you have to 
install Flask-WTF first:
```
$ pip install flask-wtf
``` 

Then initialize the CSRFProtect:
```python
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# the secret key used to generate CSRF token
app.config['SECRET_KEY'] = 'dev key' 
...
# enable CSRF protection
app.config['DROPZONE_ENABLE_CSRF'] = True  

csrf = CSRFProtect(app)
```
Make sure to set the secret key and set `DROPZONE_ENABLE_CSRF` to True. Now all the upload request 
will be protected!

We prefer to handle the CSRF error manually, because the error response's body will be displayed
as tooltip below the file thumbnail.
```python
from flask_wtf.csrf import CSRFProtect, CSRFError
...

# handle CSRF error
@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400
```

Here I use the `e.description` as error message, it's provided by CSRFProtect, one of `The CSRF token is missing` 
and `The CSRF token is invaild`. 

Try the demo application in `examples/csrf` and see 
[CSRFProtect's documentation](http://flask-wtf.readthedocs.io/en/latest/csrf.html) for more details.


Todo
-----

* A Proper Documentation
* Test
* i18n
