"""Tests of ``views.project`` functions."""

from ..tests import ModelTestCase, FunctionalTestCase


# =============================================================================
class UnitTestViewsProjectProjectView(ModelTestCase):
    """Unit test class for ``views.project.Project``."""

    # -------------------------------------------------------------------------
    def test_admin(self):
        """[u:views.project.admin]"""
        from ..views.project import ProjectView
        from ..lib.paging import Paging
        from ..lib.form import Form

        self.configurator.add_route('site_admin', '/site/admin')
        response = ProjectView(self._make_request()).admin()
        self.assertIn('form', response)
        self.assertIsInstance(response['form'], Form)
        self.assertIn('paging', response)
        self.assertIsInstance(response['paging'], Paging)
        self.assertIn('project_status', response)
        self.assertIn('active', response['project_status'])


# =============================================================================
class FunctionalTestViewProjectView(FunctionalTestCase):
    """Functional test class for ``views.project.Project``."""

    # -------------------------------------------------------------------------
    def test_not_authenticated(self):
        """[f:views.project.admin] not authenticated."""
        response = self.testapp.get('/project/admin', status=302)
        self.assertEqual(response.location,
                         'http://localhost/login?came_from=%2Fproject%2Fadmin')

    # -------------------------------------------------------------------------
    def test_not_authorized(self):
        """[f:views.project.admin] not authorized."""
        self.testapp.login('user3')
        self.testapp.get('/project/admin', status=403)

    # -------------------------------------------------------------------------
    def test_authorized(self):
        """[f:views.project.admin] authorized."""
        self.testapp.login('user1')
        self.testapp.get('/project/admin', status=200)
