import json
import py
import click

class Config():
    def __init__(self):
        self.file = py.path.local(
            click.get_app_dir('clusterone')).join('justrc.json')

    # if file does not exists create it
    # if file is corrupted and cannot be read / written inform user about this
    #TODO: TEST THIS!!!!!!!!!!

    # redo this to protected methods
    # do a generic __setattr__ and __getattr__
    def set(self, key, value):
        #TODO: Docstring

        #TODO: Smarter somethign
        #TODO: Check for existing solution
        #TODO: Context manager for json
        #TODO: Don't load and reqrite whole file, do it in a smarter way
        #TODO: Extract to utilities
        with self.file.open('w+', encoding='utf-8') as justrc:

            try:
                json_content = json.load(justrc)
            except json.decoder.JSONDecodeError as exception:
                json_content = {}

            json_content[key] = value

            try:
                # pretty printing is important for the config to be human editable
                justrc.write(json.dumps(json_content, indent=4, sort_keys=True))
            except TypeError:
                # Python 2 compliance - .write() required unicode
                justrc.write(json.dumps(json_content).decode('utf-8'))

    def get(self, key):
        # TODO: OMG, refactor like shit!!!!!!!
        try:
            with self.file.open('r', encoding='utf-8') as justrc:

                try:
                    json_content = json.load(justrc)
                except json.decoder.JSONDecodeError as exception:
                    json_content = {}
        except py.error.ENOENT:
            return None

        #TODO: This may throw, provide some sensible default mechanism
        return json_content.get(key)


    #TODO: Can this be done dynamically?
    # yup - __getattr__ or __getattribute__

    #TODO: Move validation from cmd here
    @property
    def endpoint(self):
        # TODO: Redo this to [] key aquisition
        return self.get('endpoint')

    @endpoint.setter
    def endpoint(self, value):
#TODO: Look for http URL type
#TODO: Validate if this return schema
        #type (object, str) -> str
        # TODO: Move this to function signature after dropping Python 2.7 compliance

        # TODO: Test this!!!!
        if not value.endswith('/'):
            value = "{}/".format(value)

        if not "api" in value:
            value = "{}api/".format(value)

        return self.set('endpoint', value)


CLUSTERONE_SASS_API_ENDPOINT = 'https://clusterone.com/api/'
