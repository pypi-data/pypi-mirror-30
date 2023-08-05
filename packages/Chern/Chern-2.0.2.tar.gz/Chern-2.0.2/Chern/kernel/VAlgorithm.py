""" VAlgorithm
"""
import uuid
import os
import subprocess

from Chern.kernel.VObject import VObject
from Chern.kernel.VImage import VImage
from Chern.kernel.ChernDatabase import ChernDatabase

from Chern.utils import utils
from Chern.utils.utils import color_print
from Chern.utils import git
from Chern.utils.utils import colorize

cherndb = ChernDatabase.instance()

class VAlgorithm(VObject):
    """ Algorithm class
    """
    def commit(self):
        """ Commit the object
        """
        git.add(self.path)
        commit_id = git.commit("commit all the files in {}".format(self.path))
        self.config_file.write_variable("commit_id", commit_id)
        git.commit("save the commit id")

    def impress(self):
        """ Commit the object
        """
        impression = uuid.uuid4().hex
        self.config_file.write_variable("impression", impression)
        git.add(self.path)
        git.commit("Impress: {0}".format(impression))

    def commit_id(self):
        """ Get the commit id
        """
        commit_id = self.config_file.read_variable("commit_id", None)
        if commit_id is None:
            raise Exception("")
        return commit_id

    def status(self):
        """ query the status of the current algorithm.
        """
        if not self.is_impressed():
            return "new"
        if not self.is_submitted():
            return "impressed"
        return self.image().status()

    def is_impressed(self):
        """ Judge whether impressed or not. Return a True or False.
        """
        if not self.is_git_committed():
            return False
        latest_commit_message = self.latest_commit_message()
        return "Impress:" in latest_commit_message

    def is_submitted(self):
        """ Judge whether submitted or not. Return a True or False.
        """
        if not self.is_impressed():
            return False
        return cherndb.job(self.impression()) is not None

    def submit(self):
        """ Submit """
        if self.is_submitted():
            return ["[ERROR] {0} already submitted! Skip ``submit''.".format(self.invariant_path())]
        if not self.is_impressed():
            self.impress()

        path = utils.storage_path() + "/" + self.impression()
        cwd = self.path
        utils.copy_tree(cwd, path)
        image = self.image()
        image.config_file.write_variable("job_type", "image")
        cherndb.add_job(self.impression())

    def resubmit(self):
        """ Resubmit """
        if not self.is_submitted():
            print("Job not submitted")
            return
        image = self.image()
        image.config_file.write_variable("status", "submitted")

    def stdout(self):
        """ stdout
        """
        with open(self.image().path+"/stdout") as stdout_file:
            return stdout_file.read()

    def stderr(self):
        """ Std error
        """
        with open(self.image().path+"/stderr") as stderr_file:
            return stderr_file.read()

    def image(self):
        """ Get the image. If the image is not exists raise a exception.
        """
        path = utils.storage_path() + "/" + self.impression()
        if not os.path.exists(path):
            raise Exception("")
        return VImage(path)

    def ls(self):
        """ list the infomation.
        """
        super(VAlgorithm, self).ls()
        parameters_file = utils.ConfigFile(self.path+"/.chern/parameters.py")
        parameters = parameters_file.read_variable("parameters")
        if parameters is None:
            parameters = []
        print(colorize("---- Parameters:", "title0"))
        for parameter in parameters:
            print(parameter)
        print(colorize("**** STATUS:", "title0"), self.status())
        if self.is_submitted() and self.image().error() != "":
            print(colorize("!!!! ERROR:\n", "title0"), self.image().error())
        files = os.listdir(self.path)
        for f in files:
            if not f.startswith(".") and f != "README.md":
                print(f)

    def add_parameter(self, parameter):
        """ Add a parameter to the parameters file
        """
        try:
            if parameter == "parameters":
                return ["[ERROR] A parameter is not allowed to be called ``parameters''"]
            parameters_file = utils.ConfigFile(self.path+"/.chern/parameters.py")
            parameters = parameters_file.read_variable("parameters", [])
            if parameter in parameters:
                return ["[ERROR] Fail to add parameter ``{}'', exist".format(parameter)]
            parameters.append(parameter)
            parameters_file.write_variable("parameters", parameters)
        except Exception as e:
            raise e

    def remove_parameter(self, parameter):
        """ Remove parameter
        """
        try:
            parameters_file = utils.ConfigFile(self.path+"/.chern/parameters.py")
            parameters = parameters_file.read_variable("parameters", [])
            if parameter not in parameters:
                return ["[ERROR] Fail to remove parameter ``{}'', not exist".format()]
            else:
                parameters.remove(parameter)
                return
        except Exception as e:
            raise e

def create_algorithm(path, inloop=False):
    path = utils.strip_path_string(path)
    os.mkdir(path)
    os.mkdir(path+"/.chern")
    with open(path + "/.chern/config.py", "w") as config_file:
        config_file.write("object_type = \"algorithm\"\n")
        config_file.write("main_file = \"main.py\"\n")
    with open(path + "/README.md", "w") as readme_file:
        readme_file.write("Please write README for this algorithm")
    subprocess.call("vim %s/README.md".format(path), shell=True)
    with open(path + "/main.C", "w") as main_file:
        main_file.write("""hehe""")
    subprocess.call("vim %s/main.py".format(path), shell=True)
