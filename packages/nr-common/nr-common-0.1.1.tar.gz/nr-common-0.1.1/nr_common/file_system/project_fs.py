"""Creating a project home directory."""
import logging
import os

logger = logging.getLogger(__name__)


class ProjectName(object):
    """A placeholder for default project directory."""

    def __init__(self, project_name="nr_common"):
        """Initialize project directory."""
        self.project_name = project_name

    def set_name(self, project_name):
        """Set the project name to something other than the default project name."""
        self.project_name = project_name

    def get_name(self):
        """Get the project name."""
        return self.project_name


global_project_name = ProjectName()


def set_global_project_name(project_name):
    """Set global project name."""
    global_project_name.set_name(project_name)


def get_project_directory(*subdirs):
    """Create and return project home directory."""
    project_name = global_project_name.get_name()
    project_dir = os.path.expanduser(os.path.join('~', '.{}'.format(str(project_name))))

    if subdirs:
        project_dir = os.path.join(project_dir, *subdirs)

    if not os.path.exists(project_dir):
        logger.debug("Creating project directory: {}".format(project_dir))
        os.makedirs(project_dir)

    return project_dir


def get_project_file(filename, subdirs):
    """Get project filename from project subdirs.

    Args:
        filename (str): Basename/Filename of the file.
        subdirs (list of str): List of project subdirs.

    Returns:
        str: Full path of filename.
    """
    project_dir = get_project_directory(*subdirs)
    file_path = os.path.join(project_dir, filename)
    return file_path
