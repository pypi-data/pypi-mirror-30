#!/usr/bin/env python
import tornado.web
import tornado.ioloop
import json
import os
import pwd
import sys
import click
from pybis import Openbis


class CreateNotebook(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self, whatever):
        self.send_error(400, {'message':'this webservice does not allow any GET requests. Please make a POST request with the arguments token, folder and filename. The body must contain the content of the file.'})

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def post(self, whatever):
        test = self.get_argument(name='test', default=None)

        try:
            token = self.get_argument(name='token')
            folder = self.get_argument(name='folder')
            filename = self.get_argument(name='filename')
        except Exception as e:
            self.send_error(400, {'message': str(e)})
            return

        # file-content
        content = self.request.body

        # extract username
        username, code = token.split('-')

        if test == None or test == 'False':
            test = False

        # test if openbis sessiontoken is still valid
        if not self.openbis.is_token_valid(token):
            self.send_error(401, {'message': 'token is invalid', 'token':token} )
            return

        try:
            user = pwd.getpwnam(username)
        except KeyError:
            if self.create_users_automatically:
                try: 
                    self.create_user(username)
                    user = pwd.getpwnam(username)
                except Exception:
                    self.send_error(500, {'message':"User {} cannot be created on the host system".format(username)} )
                    return
            else:
                self.send_error(401, {'message':"User {} does not exist on host system".format(username)} )
                return


        path_to_notebook = os.path.join(
            user.pw_dir, 
            folder,
            filename
        )

        # create necessary directories
        try:
            os.makedirs(os.path.dirname(path_to_notebook), exist_ok=True)
        except Exception as e:
            self.send_error(500, {'message':'unable to create directory {}: {}'.format(os.path.dirname(path_to_notebook), e)} )
            
        
        # add sequence to the filename if file already exists
        filename_name_end = filename.rfind('.')
        filename_name = filename[:filename_name_end]
        filename_extension = filename[filename_name_end:]
        filename_new = filename_name + filename_extension

        # check whether file exists
        path_to_notebook_new = os.path.join(
            user.pw_dir, 
            folder,
            filename_new
        )

        # add a number to the end of the file, if file already exists (OS X like)
        # file.ext
        # file.ext 2
        # file.ext 3
        i = 1
        while os.path.isfile(path_to_notebook_new):
            i += 1
            filename_new = filename_name + " " + str(i) + filename_extension
            path_to_notebook_new = os.path.join(
                user.pw_dir, 
                folder,
                filename_new
            )
        path_to_notebook = path_to_notebook_new
        
        link_to_notebook = {
            "fileName": filename_new,
            "path": path_to_notebook
        }
        
        # test: return without actually writing the file
        if test:
            self.write(json.dumps(link_to_notebook))
            return

        # try to write the file
        try:
            with open(path_to_notebook, 'wb') as f:
                f.write(content)
            os.chown(path_to_notebook, user.pw_uid, user.pw_gid)
            os.chmod(path_to_notebook, 0o644)
            path_to_notebook_folder = os.path.join(
                user.pw_dir, 
                folder
            )
            os.chown(path_to_notebook_folder, user.pw_uid, user.pw_gid)
            os.chmod(path_to_notebook_folder, 0o755)
        except Exception as e:
            self.send_error(500, {'message': 'unable to write file {} : {}'.format(path_to_notebook, e)} )

        self.write(json.dumps(link_to_notebook))


    def create_user(self, username):
        os.system("useradd " + username)

    def send_error(self, status_code=500, message=""):
        self.set_status(status_code)
        self.write(message)

    def initialize(self, openbis, create_users_automatically):
        self.openbis = openbis
        self.create_users_automatically = create_users_automatically
        self.set_header('Content-Type', 'application/json')


def make_app(openbis, create_users_automatically):
    """All the routing goes here...
    """
    app = tornado.web.Application([
        (r"/(.*)", CreateNotebook, {"openbis": openbis, "create_users_automatically": create_users_automatically})
    ])
    return app

@click.command()
@click.option('--port', default=8123, help='Port where this server listens to')
@click.option('--ssl-cert', '--cert', default=None, help='Path to your cert-file in PEM format')
@click.option('--ssl-key', '--key', default=None, help='Path to your key-file in PEM format')
@click.option('--openbis', required=True, help='URL and port of your openBIS installation')
@click.option('--create-users', is_flag=True, help='automatically create users, if they are not present in the system')
def start_server(port, cert, key, openbis, create_users):
    openbis = Openbis(url=openbis, verify_certificates=False)
    application = make_app(openbis=openbis, create_users_automatically=create_users)

    if cert is not None and key is not None:
        application.listen(port , ssl_options = { "certfile": cert, "keyfile":  key })
    else:
        application.listen(port);

    print("openBIS integration service started, listening on port {}".format(port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    start_server()
