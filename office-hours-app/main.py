#!/usr/bin/env python
#imports
import os
import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


#---Handlers--------------------------------------------------------------------------
class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render (self, template, **kw):
    	self.write(self.render_str(template, **kw))


#MainPage Handler -->'/'
class MainPage(BaseHandler):
	def get(self):
 		# self.render("templates/main_page.html") #TODO get rid of this maybe

        # self.render("templates/main_page.html") 
        
        #authentication of coach or student --> leads to different parts of page being rendered
        user = users.get_current_user()
        if user:

            if user.email.ends_with('@knowlabs.com'):
                #admin accessed
                greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                            (user.nickname(), users.create_logout_url('/')))
            else:
                # student accessed
                # set user to student (student is automatically an admin)
                pass
        else:
            # no one is logged in
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write('<html><body>%s</body></html>' % greeting)




        #passing all questions to main_page for loading
        question_query = Question.query()
        questions = question_query.fetch()

        template_values = {
            'questions': questions
        }


        if user.get_current_user().email.ends_with('@knowlabs.com'):
            curr_user = True
        else 
            curr_user = False
        template = jinja_env.get_template('main_page.html')
        self.response.write(template.render(template_values)) #passed questions
        self.response.write(template.render(curr_user)) #passed usertype (admin=True or student=False)



    #general post for the new question form
    def post(self):
        n_name = self.request.get('name')
        n_email = self.request.get('email')
        n_nanodegree = self.request.get('nanodegree')
        n_project = self.request.get('project')
        n_title = self.request.get('title')
        n_description = self.request.get('description')
        n_upvote = 0
        n_isCurrent = True

        n_question = Question(
            name = n_name,
            email = n_email, 
            nanodegree = n_nanodegree, 
            project = n_project, 
            title = n_title, 
            description = n_description, 
            upvote = n_upvote, 
            isCurrent = n_isCurrent)
        n_question.put()
        self.redirect('/')


    #clear all the current questions and put them to past questions
    def clearAll(self):
        #iterate through current questions and make their isCurrent value to false
        for question in questions:
            self.isCurrent = False

        self.redirect('/')

    #move the currQ to the pastQ list (called when DONE button is clicked)
    def moveToPastQ(self):
        search_key = self.question.q_id
        for question in questions:
            if(search_key == question.key):
                self.isCurrent = False
        self.redirect('/')

    #move the pastQ to the currQ list (called when REASK button is clicked)
    def moveToCurrQ(self):
        search_key = self.question.q_id
        for question in questions:
            if(search_key == question.key):
                self.isCurrent = True
        self.redirect('/')

    #no matter whether it is a currQ or pastQ, delete it (called when DELETE button is clicked)
    def deleteQ(self):
        search_key = self.question.q_id
        for question in questions:
            if(search_key == question.key):
                self.delete()
        self.redirect('/')

    #increase the Question's upvote number (called when UPVOTE button is clicked)
    def incUpvote(self):
        search_key = self.question.q_id
        for question in questions:
            if(search_key == question.key):
                self.question.q_id.upvote = self.question.q_id.upvote + 1
        self.redirect('/')


#---Objects--------------------------------------------------------------------------

#Question object; To query past or current questions use the isCurrent bool
class Question(ndb.Model):
    #Items: name, email, nanodegree, project, description
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    nanodegree = ndb.StringProperty()
    project = ndb.StringProperty()
    title = ndb.StringProperty()
    description = ndb.StringProperty()
    upvote = ndb.IntegerProperty()
    isCurrent = ndb.BooleanProperty()

    #initializes the Question object
    def __init__(self, name, email, nanodegree, project, title, description):
        self._name = name
        self._email = email
        self._nanodegree = nanodegree 
        self._project = project
        self._title = title
        self._description = description
        self._isCurrent = True



#---end---

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/display', DisplayQuestions)
], debug=True)




