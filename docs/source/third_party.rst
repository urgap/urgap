.. _third party tools:

Third party tools
#################

Overview
********

When integrating third-party tools with urgap, we recommend leveraging the container-hub repository, or your own container-hub style repository to streamline your workflow.

Container-Hub Repository
************************

The concept of the container-hub repository is to provide a convenient way to build and maintain customized containers that include your third-party software alongside urgap.

**Repository:** https://github.com/urgap/container-hub

Key Features
============

The container-hub repository offers the following benefits:

* **Automated Builds**: Containers are automatically built whenever a new urgap release is published
* **Version Tagging**: Your custom containers are automatically tagged with the corresponding urgap version
* **Latest Tag Support**: Optionally tag containers as ``latest`` to ensure changes are reflected immediately

.. important::
    When your orchestration platform references container images with the ``latest`` tag, it will pull the newest image associated with that tag whenever a deployment occurs.

    As a result, your deployments will always run the most recently built **urgap** version without manual version management. This is particularly beneficial in development and UAT environments.

Getting Started
***************

To create your own customized container:

1. Visit the container-hub repository
2. Follow the instructions to build your container with your required third-party software
3. Configure automatic builds to stay synchronized with urgap releases

This approach ensures your third-party tools remain compatible with the latest urgap versions while maintaining a clean, reproducible build process.

.. note::
    You can fork this repo and build your own container-hub if you like or contribute to the urgap-community.
