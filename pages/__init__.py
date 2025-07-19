# Import all page classes to make them easily accessible
from .splash_screen import SplashScreen
from .login_page import LoginPage
from .signup_page import SignupPage
from .dashboard_page import DashboardPage
from .media_editor_page import MediaEditorPage
from .profile_page import ProfilePage
from .help_page import HelpPage

__all__ = [
    'SplashScreen',
    'LoginPage',
    'SignupPage',
    'DashboardPage',
    'MediaEditorPage',
    'ProfilePage',
    'HelpPage'
]