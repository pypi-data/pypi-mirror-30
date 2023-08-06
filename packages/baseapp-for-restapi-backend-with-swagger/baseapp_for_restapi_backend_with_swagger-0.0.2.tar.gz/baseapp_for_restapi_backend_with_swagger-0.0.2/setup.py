from setuptools import setup
import versioneer

setup(name='baseapp_for_restapi_backend_with_swagger',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python package which provides a base application class for an app with a restapi backend that provides a swagger',
      url='https://github.com/rmetcalf9/baseapp_for_restapi_backend_with_swagger',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['src/baseapp_for_restapi_backend_with_swagger'],
      zip_safe=False)