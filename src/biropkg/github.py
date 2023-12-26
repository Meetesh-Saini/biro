from threading import Thread
import requests
from biropkg import BiroPkg


class BiroGithub(BiroPkg):
    API = "https://api.github.com"
    RAWAPI = "https://raw.githubusercontent.com"
    _REPO = ""
    _USER = ""
    _BRANCH = ""
    _DIR = ""

    def set_repo(self, user, repo, branch="main", dir="pkgs") -> None:
        self._USER = user
        self._REPO = repo
        self._BRANCH = branch
        self._DIR = dir

    def list_pkg(self):
        res = self.api(
            f"{self.API}/repos/{self._USER}/{self._REPO}/contents/{self._DIR}",
            {"ref": self._BRANCH},
        )
        if res.status_code != 200:
            return False

        return res.json()

    def get_metadata(self, pkg_list, callback):
        for package in pkg_list:
            package_name = package["name"]
            package_url = f"{self.RAWAPI}/{self._USER}/{self._REPO}/{self._BRANCH}/{self._DIR}/{package_name}"
            self.api(
                f"{package_url}/meta.yml",
                Async=True,
                callback=callback,
                package_name=package_name,
                fetch_url=f"{package_url}/{package_name}.biro",
            )
            print(f"\tFetching {package_name}")

    def api(
        self,
        route,
        params=None,
        Async=False,
        callback=None,
        package_name=None,
        fetch_url=None,
        *args,
        **kwargs,
    ):
        if not Async:
            return requests.get(route, params=params, *args, **kwargs)

        if callback:

            def callback_with_args(response, *args, **kwargs):
                callback(
                    response, package_name=package_name, fetch_url=fetch_url
                )

            kwargs["hooks"] = {"response": callback_with_args}
        thread = Thread(target=requests.get, args=(route, *args), kwargs=kwargs)
        thread.start()
