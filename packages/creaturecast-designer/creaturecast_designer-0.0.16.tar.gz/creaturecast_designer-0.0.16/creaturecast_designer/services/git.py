
class GitFetchWorker(QThread):

    update_progress = Signal(int)
    failed = Signal()
    success = Signal()
    def __init__(self, *args, **kwargs):
        self.git_url = str(args[0])
        QThread.__init__(self)

    def run(self):

        import git
        from git import RemoteProgress

        module_name = self.git_url.split('/')[-1].split('.')[0]
        package_directory = '%s/%s' % (env.modules_directory, module_name)
        outdir_checker = package_directory + '/.git'

        class ProgressHandler(RemoteProgress):
            update_progress = PySignal.ClassSignal()

            def __init__(self, signal, *args, **kwargs):
                self.signal = signal
                super(ProgressHandler, self).__init__(*args, **kwargs)

            def update(self, op_code, cur_count, max_count=None, message=''):
                self.signal.emit(int(float(cur_count) / (max_count or 100.0) * 100))

        progress_handler = ProgressHandler(self.update_progress)


        if os.path.exists(outdir_checker):
            #repo_worker = git.Repo.init(package_directory)
            #repo_worker.git.reset('--hard')
            #repo_worker.git.clean('-fdx')
            #remotes = repo_worker.remotes
            #for r in remotes:
            #    o = r.origin
            #    o.pull(progress=progress_handler)
            self.success.emit()

        if not os.path.exists(outdir_checker):
            shutil.rmtree(package_directory, ignore_errors=True)
            os.makedirs(package_directory)
            try:
                git.Repo.clone_from(self.git_url, package_directory, progress=progress_handler)
            except:
                self.failed.emit()
                print 'Failed to clone repo. There seems to be a problem with the network connection'
            print('git dir created')


class UninstallWorker(QThread):

    failed = Signal()
    success = Signal()

    def __init__(self, *args, **kwargs):
        self.package_directory = copy.copy(str(args[0]))
        QThread.__init__(self)

    def run(self):
        if not os.path.exists(self.package_directory):
            self.success.emit()
        #clear_dir(self.package_directory)
        self.success.emit()
