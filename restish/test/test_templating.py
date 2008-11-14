import unittest
from webob import Request

from restish import templating


class TestModule(unittest.TestCase):

    def test_exports(self):
        """
        Test that default rendering methods are available at module scope.
        """
        keys = dir(templating)
        assert 'render' in keys
        assert 'page' in keys
        assert 'element' in keys


class TestRenderingArgs(unittest.TestCase):

    def test_args(self):
        """
        Test that common rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.args(request)
        assert set(['url']) == set(args)

    def test_element_args(self):
        """
        Test that element rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.element_args(request, None)
        assert set(['url', 'element']) == set(args)

    def test_page_args(self):
        """
        Test that page rendering args are correct.
        """
        rendering = templating.Rendering()
        request = Request.blank('/')
        args = rendering.page_args(request, None)
        assert set(['url', 'element']) == set(args)

    def test_args_chaining(self):
        """
        Test that an extra common arg is also available to elements and pages.
        """
        class Rendering(templating.Rendering):
            def args(self, request):
                args = super(Rendering, self).args(request)
                args['extra'] = None
                return args
        rendering = Rendering()
        request = Request.blank('/')
        assert set(['url', 'extra']) == set(rendering.args(request))
        assert set(['url', 'element', 'extra']) == set(rendering.element_args(request, None))
        assert set(['url', 'element', 'extra']) == set(rendering.element_args(request, None))


OUTPUT_DOC = """<div><p>url.abs: /</p><p>&lt;strong&gt;unsafe&lt;/strong&gt;</p><p><strong>safe</strong></p></div>"""


class _TemplatingEngineTestCase(unittest.TestCase):

    renderer = None

    def test_templating(self):
        environ = {'restish.templating.renderer': self.renderer}
        request = Request.blank('/', environ=environ)
        doc = templating.render(request, 'who-cares.html', {
            'unsafe': '<strong>unsafe</strong>',
            'safe': '<strong>safe</strong>',
            })
        print doc
        assert doc == OUTPUT_DOC


try:
    import mako.template
    class TestMako(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = mako.template.Template("""<div><p>url.abs: ${url.abs|h}</p><p>${unsafe|h}</p><p>${safe}</p></div>""")
            return template.render(**args)
    class TestMakoAutoEscape(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = mako.template.Template("""<div><p>url.abs: ${url.abs}</p><p>${unsafe}</p><p>${safe|n}</p></div>""", default_filters=['h'])
            return template.render(**args)
except ImportError:
    print "Skipping Mako tests"


try:
    import genshi.template
    class TestGenshi(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = genshi.template.MarkupTemplate("""<div><p>url.abs: ${url.abs}</p><p>${unsafe}</p><p>${Markup(safe)}</p></div>""")
            return template.generate(**args).render('html')
except ImportError:
    print "Skipping Genshi tests"


try:
    import jinja2
    class TestJinja2(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = jinja2.Template("""<div><p>url.abs: {{ url.abs|e }}</p><p>{{ unsafe|e }}</p><p>{{ safe }}</p></div>""")
            return template.render(**args)
    class TestJinja2AutoEscape(_TemplatingEngineTestCase):
        @staticmethod
        def renderer(template, args={}):
            template = jinja2.Template("""<div><p>url.abs: {{ url.abs }}</p><p>{{ unsafe }}</p><p>{{ safe|safe }}</p></div>""", autoescape=True)
            return template.render(**args)
except ImportError:
    print "Skipping Jinja2 tests"


if __name__ == '__main__':
    unittest.main()
