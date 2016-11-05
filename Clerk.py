'''

    By: Rohan Mehta
    For: Minimilistic Web Devs
    Prereq: weurzueg, redis

'''


import redis
import os
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug import utils
from werkzeug.wrappers import Request,Response
from clerk.template_engine import Compiler
import json
import re

class Clerk(object):
    ##app definintions
    not_found_404 = "HELLO WORLD, this 'Clerk' Project is working!"
    urls = []
    template_folder = "templates/"
    static_folder = "static"
    port = 5000
    host = '127.0.0.1'

    #create serving app
    def create_app(redis_host='localhost', redis_port=6379, with_static=True):
        app = Shortly({
            'redis_host': redis_host,
            'redis_port': redis_port
        })

        if with_static:
            app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/static': os.path.join(os.path.dirname(__file__), 'static')
            })
        return app

    #serve function to run website
    def serve(self, app, host='127.0.0.1', port=port):
        from werkzeug.serving import run_simple

        run_simple(self.host, self.port, app, use_debugger=True, use_reloader=True)


    def config(self,not_found_404,template_folder,static_folder,port=5000):
        self.not_found_404 = not_found_404
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.port = port
class Page(Clerk):
    #pages html
    html = "<h1>Hello World</h1>"
    embedables = {}
    type = "html"

    url = None
    
    file_path = None
    file_name = None


    #set html of page in string form
    def set_html(self,text):
        self.html = text

    #set page's html from template
    def set_template(self,name):
        self.file_path = str(self.template_folder) +"/"+ str(name)
        self.file_name = name
        file = open(self.file_path, "r")
        self.html = file.read()

    #FOR CLERK TEMPLATING ENGINE PLUGINS
    def embed(self,embed):
        self.embedables =  embed     
    def load_html(self):
        print(self.file_path)
        file = open(self.file_path, "r")
        self.html = file.read()
        return self.html

    def handle_dyn_url(self,value):
        pass

class StaticPage(Page):
    
    def set_static(self,name_path):
        self.path = str(self.static_folder) + "/" + str(name_path)
        file = open(self.path,"r")
        self.html = file.read()

    def load_html(self):
        file = open(self.path, "r")
        self.html = file.read()
        return self.html

class Serializer(Page):
    type = "json"

    def give_data(self,data):
        
        data_html = json.dumps(data,    indent=4,   sort_keys="True")
        
        self.html = str(data_html)

class ContentPage(Page):
    pass

class FormPage(Page):
    #page to redirect to once form is rendered
    redirect_url = None

    #fields from form to look for
    fields = []

    #function to run once data is collected
    form_proccessor = None

    #function to create instance
    def create(self,redirect_page,fields):
        self.fields = fields
        self.redirect_page = redirect_page

    def conduct_redirect(self):
        print("REDIRECTING")
        utils.redirect(self.redirect_url)

class Shortly(Clerk):

    #DEFINE REDIS TOOLS
    def __init__(self, config):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'])


    #SERVE HTML
    def dispatch_request(self, request):
        #define vars for redis
        self.host = request.url_root
        self.url = request.url
        self.host_len = len(self.host)
        self.queriedPage = self.url[self.host_len-1:]

        #var to keep trac for returning 404 page
        self.found = False

        #loop through each page 
        for self.page in self.urls:
            #get pages url
            self.url = self.page.url
            #is the url for page equal to page user is looking for
            if [] != re.findall(self.url,self.queriedPage):
                #stop any 404's from returning
                self.found = True

                # var for page being used currently
                self.current_page = self.page

                #condct dyn urls func
                self.current_page.handle_dyn_url(self.queriedPage)

                #if user is submiting a form
                if request.method == "POST":

                    #process form
                    self.post_process(request,self.current_page)

                    #make redirect page
                    self.current_page = self.current_page.redirect_page()
                    ###self.current_page.conduct_redirect()
                
                
                self.cleaned_html = self.html_prep(self.current_page) 



                #return prettified html to user
                return Response(self.cleaned_html,mimetype='text/'+self.current_page.type)

        if self.found == False:
            return Response(self.not_found_404, mimetype='text/html')

    #DEFINE HTML DISPLAY
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    #function to collect info from form
    def post_process(self,request,current_page):
        # create empyty dict to hold new form
        self.form_fields = {}

        # add form names that user gave us to the dict
        for self.field in current_page.fields:
            # set equal to None
            self.form_fields[self.field] = ""


        # for fields page is returning
        for self.html_field in request.form:
            # for fields user is looking for
            for self.user_field in self.form_fields:
                # if field return and field user wanted are the same
                if self.user_field == self.html_field:
                    # write it into returning dict returned to user
                    self.form_fields[self.user_field] = request.form[self.user_field]

        current_page.form_proccessor(self.form_fields)

    def html_prep(self,page):

        # get raw html
        if self.current_page.type == "html":
            pre_html = self.current_page.load_html()
            # get any embedables for page
            embedables = self.current_page.embedables

            # have temp_eng look for static tags
            embedables["static"] = "../"+self.static_folder

            # get prettified html
            serve_html = Compiler.compile(pre_html, embedables)

        elif self.current_page.type == "json":
            serve_html  = self.current_page.html
        else:
            serve_html = self.current_page.load_html()

        return serve_html
    #DEFINE WSGI APP SETTINGS
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

