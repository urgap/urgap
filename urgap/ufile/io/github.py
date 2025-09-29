"""Github subclass of urgap2's UIO submodule."""

import logging
import re
import uuid

from typing import ParamSpec

import requests

from github import Auth, Github, GithubException

from urgap.ufile.io._base import UIOBase

P = ParamSpec("P")
logger = logging.getLogger(__name__)


class IOGithub(UIOBase):
    """UIO Class interface for Github file objects."""

    def __init__(self, **kwargs: P.kwargs) -> None:
        """Create new UIO class for processing Github scheme.

        Args:
            **kwargs: Requires parsed_uri key to set respective attributes.

        github://<github_host>/<org_name>/<repo_name>/<branch>#path/to/dir/<object_name>
        """
        super().__init__(**kwargs)
        self.query_params = self.uuri.query

        org_name = self.uuri.get_github_resource_name("org")
        repo_name = self.uuri.get_github_resource_name("repo")
        self.repo_full_name = org_name + "/" + repo_name
        self.branch_name = self.uuri.get_github_resource_name("branch")
        self.object_filepath = self.uuri.fragment
        try:
            cred_key = f"{self.uuri.scheme}://{self.uuri.netloc}/{self.repo_full_name}"
            password = self.uuri.password
            if password is None:
                # Can access only public repos
                self.github_io = Github()
            else:
                # Can access private repos too
                self.github_io = Github(auth=Auth.Token(password))
            self.repo = self.github_io.get_repo(self.repo_full_name)
        except GithubException as e:
            msg = f"Incorrect/no credentials found for {cred_key} - if needed, please supply!"
            logger.exception(msg)
            raise KeyError(msg) from e

        available_branches = [x.name for x in self.repo.get_branches()]
        if self.branch_name not in available_branches:
            msg = (
                f"Branch '{self.branch_name}' in not available on host {self.uuri.netloc}"
                f". Available branches are: {sorted(available_branches)}"
            )
            raise OSError(msg)

        self.source_branch = self.repo.get_branch(self.branch_name)

        self.target_branch_name = self.query_params.get(
            "target-branch",
            f"feature/new_ufile_{str(uuid.uuid4())[:8]}",
        )

    def __del__(self) -> None:
        """Close Github IO connection on object deletion."""

    @property
    def remote_path(self) -> str | None:
        """Get remote file path.

        Returns:
            URL of remote file.
        """
        if self.remote_object_exists() is True:
            return self.repo.get_contents(
                self.object_filepath,
                ref=self.source_branch.name,
            ).url
        return None

    def get_file_properties(self) -> dict | None:
        """Get properties associated with referenced file.

        Returns:
            Properties of file.
        """
        if self.remote_object_exists() is True:
            return self.repo.get_contents(
                self.object_filepath,
                ref=self.source_branch.name,
            ).path
        return None

    def get_remote_tags(self) -> dict | None:
        """Get remote tags associated with referenced file.

        Returns:
            Remotely stored tags.
        """
        if self.remote_object_exists() is True:
            tags = self.repo.get_contents(
                self.object_filepath,
                ref=self.source_branch.name,
            ).raw_data
            tags.pop("content")
            return tags
        return None

    def get_object(self) -> str | None:
        """Get Github file for referenced URI.

        Returns:
            File path on github repo.
        """
        if self.remote_object_exists() is True:
            return self.repo.get_contents(
                self.object_filepath,
                ref=self.source_branch.name,
            ).path
        return None

    def download(self) -> None:
        """Download referenced remote object.

        Object is written to local scratch path.
        """
        try:
            download = self.repo.get_contents(
                self.object_filepath,
                ref=self.source_branch.name,
            )
            text = download.decoded_content.decode("utf-8")

            with self.scratch_path.open("w", encoding="utf-8") as f:
                f.write(text)
        except GithubException as e:
            self.scratch_path.unlink(missing_ok=True)
            raise RuntimeError from e

    def upload(self, tags: dict | None = None) -> None:
        """Upload local object from scratch to the github remote branch and create a PR."""
        msg = f"tags will be skipped. {tags}!"
        logger.warning(msg)
        target_ref = f"refs/heads/{self.target_branch_name}"
        self.repo.create_git_ref(ref=target_ref, sha=self.source_branch.commit.sha)
        commit_message = "New ufile is available"
        upload_content = None
        with self.scratch_path.open("rb") as f:
            upload_content = f.read()
        if self.remote_object_exists():
            original_file_sha = self.repo.get_contents(
                self.object_filepath,
                self.source_branch,
            ).sha
            try:
                self.repo.update_file(
                    path=self.object_filepath,
                    message=commit_message,
                    content=upload_content,
                    sha=original_file_sha,
                    branch=self.target_branch_name,
                )
            except GithubException as e:
                msg = f"Failed to update the ufile: {e}!"
                logger.exception(msg)
                raise RuntimeError(msg) from e
        else:
            try:
                self.repo.create_file(
                    path=self.object_filepath,
                    message=commit_message,
                    content=upload_content,
                    branch=self.target_branch_name,
                )
            except GithubException as e:
                msg = f"Failed to add the ufile: {e}!"
                raise RuntimeError(msg) from e
        try:
            pr = self.repo.create_pull(
                title=commit_message,
                body="This pull request adds a new ufile.",
                head=self.target_branch_name,
                base=self.source_branch.name,
            )
            msg = f"PR #{pr.number} is created"
            logger.info(msg)
        except GithubException as e:
            msg = f"Unable to create pull request. {e}!"
            raise RuntimeError(msg) from e

    def remote_object_exists(self) -> bool:
        """Verify referenced remote object exists.

        Returns:
            True if remote object exists.
        """
        try:
            self.repo.get_contents(self.object_filepath, ref=self.source_branch.name)
        except GithubException as e:
            msg = f"Unable to find {self.object_filepath}. {e}!"
            logger.info(msg)
            return False
        return True

    def _remote_path_exists(self) -> bool:
        """Verify referenced remote path exists.

        Returns:
            True if remote path exists.
        """
        return self.remote_object_exists()

    def list_container_items(
        self,
        pattern: str | None = None,
        full_string: bool = True,
    ) -> list:
        """Get objects in folder/'container'.

        Can be filtered by regex pattern.

        Args:
            pattern: Regex pattern for filtering.
            full_string: Whether to return the list with full strings or just fragments.

        Returns:
            List of object names after filtering.
        """
        url = f"https://api.github.com/repos/{self.repo_full_name}/git/trees/{self.branch_name}?recursive=1"
        headers = (
            {"Authorization": f"token {self.uuri.password}"}
            if self.uuri.password is not None
            else {}
        )
        resp = requests.get(url, headers=headers)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            msg = f"Error connecting to GitHub API: {resp.status_code} {resp.text}"
            logger.exception(msg)
            raise OSError(msg) from e
        tree = resp.json().get("tree")
        if tree is None:
            msg = "Could not obtain 'tree' structure from repository."
            logger.error(msg)
            raise KeyError(msg)
        container_objects = [
            f"{self.uuri.scheme}://{self.uuri.netloc}/{self.repo_full_name}/{self.branch_name}#{item['path']}"
            for item in tree
            if item["type"] == "blob"
        ]
        if pattern is not None:
            container_objects = [
                f for f in container_objects if re.search(pattern, f) is not None
            ]
        if full_string is True:
            return container_objects
        logger.warning(
            "DeprecationWarning: list_container_items with full_string=False will be deprecated soon, use full_string=True instead.",
        )
        return [obj.split("#")[1] for obj in container_objects]