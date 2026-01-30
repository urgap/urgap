.. _getting_started:

Concepts
==========

File Identity
--------------

In file-centric pipelines, identity serves as the anchor and is indispensable 
in cloud-native systems. To make it simple and portable, we introduce the 
:class:`urgap.UFile` and its associated urgap canonical file signature (`ucfs`), 
inspired by ISBNs for books. Just as the same title can live in many bookstores 
yet keep one identifier, `ucfs` lets identical data objects exist across storage 
backends and clouds while preserving identity. A ucfs combines the object name 
and a content hash, e.g. ``<object_name>@<md5>``.

:class:`urgap.UFile` uses standard URIs and assigns the object name 
to the fragment: ``<schema>://<location>#<object_name>``

The checksum is provided as a URI query parameter or as metadata tags. 
The hash algorithms are pluggable, e.g., MD5 or blake2. By separating where 
an object lives from what it is, urgap makes file identity location-agnostic, 
enabling seamless retrieval and equality checks across clouds, simplifies 
migration, and lays the groundwork for a data cataloging, file mesh and 
discovery layer that exceeds traditional storage boundaries.

Provenance as Code (PaC)
----------------------------

Provenance, lineage, and reproducibility sit at the core of modern workflows.
We adopt Provenance as Code (PaC), a paradigm where lineage is embedded directly
in the processing architecture rather than bolted on afterward.

Unlike traditional systems that record provenance through separate system stores, PaC encodes
key lineage into the output filename. In urgap, users and pipelines do not choose
output names. Each name is a deterministic digest of the processing parameters
that affect results, the algorithm and its version, and the input file signatures
(the list of `ucfs`, see below and :numref:`Figure 1`). The result is an immutable PaC hash
that supports global smart rerun and reproducibility. Files in different locations
are treated as the same asset if their `ucfs` match, enabling identity-based reuse
across environments. This design plays well with explicit pipeline specs,
reproducible forks, and a data-mesh style where files are referenced by signature
and resolved to physical locations through a decentralized, optionally customizable
resolver.

.. raw:: html

   <div style="text-align: center;">

.. image:: figs/PaC.png
   :alt: Provenance as Code flow with deterministic signatures
   :width: 60%
   :name: Figure 1

.. raw:: html

   </div>

**Figure 1: Provenance as Code (PaC).**  
**a)** Three elements feed the PaC hash for an output: i) the input files' urgap canonical file signatures (ucfs, green), ii) the resource identifier (red), and iii) only those parameters that affect results (e.g., not thread counts, purple).  
**b)** Changing a result-affecting parameter yields a different parameter digest and thus a different PaC hash.


Forking from an existing pipeline or defining one without knowing what outputs
already exist, urgap will skip steps whose outputs are already present. The encoded
provenance inherently supports the FAIR principles (Findable, Accessible,
Interoperable, Reusable), as every asset carries its own lineage, making it
self-describing and easier to govern without extra workload. Additionally, urgap
tracks the lineage tree in ufile tags.

Since the PaC hash cannot directly be mapped back to execution details,
additional run metadata has to be recorded elsewhere if required. Such a metadata
storage capability is also implemented in urgap as `urgap.umeta` and is populated
automatically during and after execution, tracking e.g. execution times and
user-defined metrics. For end-to-end visibility, urgap also exports traces using
the OpenTelemetry standard.

Unode
----------

The :class:`urgap.unode` class is the heart of our processing abstraction. 
It turns standalone tools into standardized nodes and those into containerized microservices. 
By encapsulating tools with an urgap unode, developers can rely on robust and established data I/O, 
secret handling, metadata plumbing and thus they can focus on the data engineering logic.

Since development starts with a containerized tool, a lightweight :class:`urgap.unode` wrapper in addition 
to the urgap runtime converts any container with a tool into a standardized microservice that can be 
used in the same standardized way as all tools and across ecosystems. The result is a set of encapsulated 
units with consistent interfaces, easy to deploy, orchestrate, and monitor in any environment.

Frameworks live or die by low adoption friction. In `urgap`, that's the role of the `unode`, a thin 
layer that bridges a resource and the framework. A :class:`urgap.unode` adapts inputs, outputs and 
assembles the tool's command line, removing the need to write glue code.

Ufiles
----------


Uctl
----------


Smart rerun logic
----------

Standardized metadata and complete lineage enable "smart rerun" logic that detects when a computation would 
reproduce an existing result and safely skips or reuses work (:numref:`Figure 2`). Embedding provenance into processing 
frameworks and applying execution-time optimization preserves analytical flexibility while curbing costs at scale.


.. raw:: html

   <div style="text-align: center;">

.. image:: figs/RerunLogic.png
   :alt: Examples of smart rerun logic
   :name: Figure 2
   :width: 60%

.. raw:: html

   </div>

**Figure 2: Examples of smart rerun logic.**
**(a)** A typical NGS pipeline runs quality control and adapter trimming, indexes the reference genome, aligns reads, sorts and marks duplicates, then performs final QC.
**(b)** When reprocessing with different alignment parameters, steps upstream of alignment (QC/trimming, indexing) are reused and skipped. Only alignment and downstream steps are rerun (grey indicates skipped).
**(c)** Generalized cases across tools and pipelines: 
*Top:* an initial run from Dataset A produces B (tool V) and C (tool W). 
*Middle:* extending the analysis to create D (tool X) runs only X, while V and W are skipped. 
*Bottom:* a forked pipeline still reuses V (skipped) but extends to X then W, so those two are executed to produce E and F.

The payoff becomes even more striking when evaluating novel processing methods. The ability to introduce a new processing 
node into an existing pipeline, replace outdated nodes, and keep the rest of the data workflow graph intact adds significant 
value with little overhead. With smart rerun logic, results from competing approaches can be compared on the same inputs 
without requiring parallel pipelines, or duplicated effort allowing for data-driven adoption decisions and a lower associated risk.

In a research context, this approach accelerates discovery by reducing prototyping timelines and promotes FAIR principles. 
Urgap's smart rerun logic and standardized interfaces enable seamless experimentation when researchers substitute pipeline 
components without redundant computation. The framework scales efficiently with growing cohort complexity while reducing 
environmental impact through systematic reuse of analytical products.