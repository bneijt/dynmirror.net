
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

class TemplateRendering:
  __jinja_template_loader = FileSystemLoader([os.path.join(os.path.dirname(__file__), 'templates')])
  
  def render_to_response(self, template_name, environment):
    env = Environment(loader = self.__jinja_template_loader)
    try:
      template = env.get_template(template_name)
    except TemplateNotFound:
      return self.not_found()
    if not environment.has_key('request'):
      environment['request'] = self.request
    content = template.render(environment)
    return self.response.out.write(content)

  def not_found(self, msg = None):
    self.response.set_status(404)
    #TODO make self.render_to_response here
    if msg:
      self.response.out.write(msg)
    else:
      self.response.out.write('404 Not found')
    return
