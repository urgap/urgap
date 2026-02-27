.. _third party tools:

Third party tools
#################

Overview
********

When integrating third-party tools with urgap, we recommend leveraging the container-hub repository to streamline your workflow.

Container-Hub Repository
************************

The container-hub repository provides a convenient way to build and maintain customized containers that include your third-party software alongside urgap.

**Repository:** https://github.com/urgap/container-hub

Key Features
============

The container-hub repository offers the following benefits:

* **Automated Builds**: Containers are automatically built whenever a new urgap release is published
* **Version Tagging**: Your custom containers are automatically tagged with the corresponding urgap version
* **Latest Tag Support**: Optionally tag containers as ``latest`` to ensure changes are reflected immediately

.. important::
   When your pipeline uses the ``latest`` image tag, it will be automatically updated on each image pull.
   This is particularly useful in orchestration platforms like Kubernetes, where pulling the latest tag
   ensures your deployments always use the most recent urgap version without requiring manual intervention.

Getting Started
***************

To create your own customized container:

1. Visit the container-hub repository
2. Follow the instructions to build your container with your required third-party software
3. Configure automatic builds to stay synchronized with urgap releases

This approach ensures your third-party tools remain compatible with the latest urgap versions while maintaining a clean, reproducible build process.
