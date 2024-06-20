
import json
import logging
import tempfile



class IOOmiq(UIOBase):


        Args:
        """
        self._omiq_user_info = None
        self._file_id = None
        self._tags = None

        password = um.get_password(cred_key)
        user = um.get_user(cred_key)
        with tempfile.NamedTemporaryFile() as fp:
                json.dump(
                    {
                        "token": password,
                        "email": user,
                    },
                    tmp_file,
                )
            self._omiq_user_info = self._api.get_user()
            if self._omiq_user_info is not None:
                )
    @property

        Returns:
        """
        return None

    @property

        Returns:
        """
        return None


        Returns:
        """
        if self._tags is not None:
            return self._tags

        keys_to_grab = [
            "id",
            "datasetId",
            "fileName",
            "displayName",
            "rawFileBlobId",
            "jobName",
            "status",
            "size",
        ]
        self._tags = {"omiq_tags": True}
        for file_dict in self._list_files_in_dataset():
                for key in keys_to_grab:
                    file_value = file_dict.get(key, None)
                    if file_value is None:
                    self._tags[key] = file_dict.get(key, None)
        return self._tags

    def download(self) -> None:
    @property
    def file_id(self) -> int:
        tags = self.get_remote_tags()
        return tags["id"]


    def list_container_items(
        self,
    ) -> list:

        Args:

        Returns:
        """
        if pattern is not None:
            container_objects = [
                name
                for name in container_objects
                if re.search(pattern, name) is not None
            ]
        return container_objects

    def remote_object_exists(self) -> bool:

        Returns:
        """