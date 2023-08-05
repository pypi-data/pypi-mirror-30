import git
import getpass
import shutil


class HerokuGitFS:
    def __init__(self, remote_url, directory, branch, keep_history=False):
        """
        Initiate a new gitFS folder.

        :param branch: The branch to push and commit changes to
        :type branch: str
        :param remote_url: The remote URL for the branch
        :type remote_url: str
        :param directory: The directory to clone to
        :type directory: str
        :param keep_history: If set to True, then the git repository will not be orphaned on each new commit.
        :type keep_history: bool
        """
        self.remote_url = remote_url  #: The remote URL of the repository
        self.directory = directory  #: The directory used by HerokuGitFS
        self.keep_history = keep_history  #: If this is True, the repository will not be orphaned.
        self.branch = branch  #: The branch to use and push to.
        self.repo = git.Repo.clone_from(url=remote_url, to_path=directory)  #: :any:git.Repo object to do operations on.
        print('Sucessfully initialized {0} from the git repo'.format(directory))
        self.repo.git.remote(['rm', 'origin'])
        self.repo.git.checkout(['-B', branch])
        print('Checked out branch {0}'.format(self.branch))

    def commit(self, message='No message given.', username=None, email='dummy@email.com'):
        """
        Create a new commit. If the keep_history attribute is set to False, the branch will be orphaned.

        :param message: The commit message.
        :type message: str
        :param username: The name to commit with, defaults to the current user.
        :type username: str
        :param email: The email to commit with, defaults to a dummy email.
        :type email: str
        """
        if username is None:
            username = getpass.getuser()

        if not self.keep_history:
            self.repo.git.checkout(['--orphan', 'temp'])

        self.repo.git.config(['user.name', username])
        self.repo.git.config(['user.email', email])
        self.repo.git.add('-A')
        self.repo.git.commit(['--message', message])

        if not self.keep_history:
            self.repo.git.branch(['-M', 'temp', self.branch])

    def push(self, remote_url=None):
        """
        Push the commit to the remote.

        :param remote_url: The remote URL to push for. If left empty, the init URL is used
        :type remote_url: str
        :raise Exception: Pushing the code to the remote failed.
        """
        if remote_url is None:
            remote_url = self.remote_url
        try:
            self.repo.git.push(['--force', remote_url, self.branch])
        except Exception as e:
            raise e

    def update(self, message='No message given.', username=None, email='dummy@email.com'):
        """
        Wrapper around commit and push.

        :param message: Message to commit with, defaults to No message given.
        :type message: str
        :param username: The name to commit with, defaults to the current user.
        :type username: str
        :param email: The email to commit with, defaults to a dummy email.
        :type email: str
        """
        if username is None:
            username = getpass.getuser()
        self.commit(message=message, username=username, email=email)
        self.push()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Nulls the repo and branch attributes and removes the git directory. Also called by __exit__, although you'll need to set the object to None manually if you call
        close() yourself.

        It should be obvious that after this call, you should no longer use commit() or push() .

        :raises Exception: Any exceptions raised by removing the directory.
        """
        try:
            shutil.rmtree(self.directory)
        except Exception as e:
            raise e
        self.repo = None
        self.branch = None
