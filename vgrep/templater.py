from jinja2 import Environment, PackageLoader, select_autoescape


class Templater:
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("vgrep"),
            autoescape=select_autoescape()
        )

    def render_template(self,
                        template_name: str,
                        **params):
        template = self.env.get_template(template_name)

        return template.render(**params)
