====
`gnpy`: mesh optical network route planning and optimization library
====

|docs| |build|

**gnpy is an open-source, community-developed library for building route planning
and optimization tools in real-world mesh optical networks.**

`gnpy <http://github.com/telecominfraproject/gnpy>`_ is:

- a sponsored project of the `OOPT/PSE <http://telecominfraproject.com/project-groups-2/backhaul-projects/open-optical-packet-transport/>`_ working group of the `Telecom Infra Project <http://telecominfraproject.com>`_.
- fully community-driven, fully open source library
- driven by a consortium of operators, vendors, and academic researchers
- intended for rapid development of production-grade route planning tools
- easily extensible to include custom network elements
- performant to the scale of real-world mesh optical networks

Documentation: https://gnpy.readthedocs.io

Installation
------------

``gnpy`` is hosted in the `Python Package Index <http://pypi.org/>`_ (`gnpy <https://pypi.org/project/gnpy/>`_). It can be installed via:

.. code-block:: shell

    $ pip install gnpy

It can also be installed directly from the repo.

.. code-block:: shell

    $ git clone https://github.com/telecominfraproject/gnpy
    $ cd gnpy
    $ python setup.py install

Both approaches above will handle installing any additional software dependencies.

    **Note**: *We recommend the use of the Anaconda Python distribution
    (https://www.anaconda.com/download) which comes with many scientific
    computing dependencies pre-installed.*

Instructions for Use
--------------------

``gnpy`` is a library for building route planning and optimization tools.

It ships with a number of example programs. Release versions will ship with
fully-functional programs.


    **Note**: *If you are a network operator or involved in route planning and
    optimization for your organization, please contact project maintainer James
    Powell <james.powell@telecominfraproject>. gnpy is looking for users with
    specific, delineated use cases to drive requirements for future
    development.*


**To get started, run the transmission example:**

.. code-block:: shell

    $ python examples/transmission_main_example.py

By default, this script operates on a single span network defined in `examples/edfa/edfa_example_network.json <examples/edfa/edfa_example_network.json>`_

You can specify a different network at the command line as follows. For
example, to use the CORONET Continental US (CONUS) network defined in `examples/coronet_conus_example.json <examples/coronet_conus_example.json>`_:

.. code-block:: shell

    $ python examples/transmission_main_example.py examples/coronet_conus_example.json

This script will calculate the average signal osnr and snr across 93 network
elements (transceiver, ROADMs, fibers, and amplifiers) between Abilene, Texas
and Albany, New York.

This script calculates the average signal OSNR = |OSNR| and SNR = |SNR|.

.. |OSNR| replace:: P\ :sub:`ch`\ /P\ :sub:`ase`
.. |SNR| replace:: P\ :sub:`ch`\ /(P\ :sub:`nli`\ +\ P\ :sub:`ase`)

|Pase| is the amplified spontaneous emission noise, and |Pnli| the non-linear
interference noise.

.. |Pase| replace:: P\ :sub:`ase`
.. |Pnli| replace:: P\ :sub:`nli`

The `transmission_main_example.py <examples/transmission_main_example.py>`_
script propagates a specrum of 96 channels at 32 Gbaud, 50 GHz spacing and 0
dBm/channel. These are not yet parametrized but can be modified directly in the
script (via the SpectralInformation tuple) to accomodate any baud rate,
spacing, power or channel count demand.

The amplifier's gain is set to exactly compsenate for the loss in each network
element. The amplifier is currently defined with gain range of 15 dB to 25 dB
and 21 dBm max output power. Ripple and NF models are defined in
`examples/edfa_config.json <examples/edfa_config.json>`_

Contributing
------------

``gnpy`` is looking for additional contributors, especially those with experience
planning and maintaining large-scale, real-world mesh optical networks.

To get involved, please contact James Powell
<james.powell@telecominfraproject.com> or Gert Grammel <ggrammel@juniper.net>.

``gnpy`` contributions are currently limited to members of `TIP
<http://telecominfraproject.com>`_. Membership is free and open to all.

See the `Onboarding Guide
<https://github.com/Telecominfraproject/gnpy/wiki/Onboarding-Guide>`_ for
specific details on code contribtions.

See `AUTHORS.rst <AUTHORS.rst>`_ for past and present contributors.

Project Background
------------------

Data Centers are built upon interchangeable, highly standardized node and
network architectures rather than a sum of isolated solutions. This also
translates to optical networking. It leads to a push in enabling multi-vendor
optical network by disaggregating HW and SW functions and focussing on
interoperability. In this paradigm, the burden of responsibility for ensuring
the performance of such disaggregated open optical systems falls on the
operators. Consequently, operators and vendors are collaborating in defining
control models that can be readily used by off-the-shelf controllers. However,
node and network models are only part of the answer. To take reasonable
decisions, controllers need to incorporate logic to simulate and assess optical
performance. Hence, a vendor-independent optical quality estimator is required.
Given its vendor-agnostic nature, such an estimator needs to be driven by a
consortium of operators, system and component suppliers.

Founded in February 2016, the Telecom Infra Project (TIP) is an
engineering-focused initiative which is operator driven, but features
collaboration across operators, suppliers, developers, integrators, and
startups with the goal of disaggregating the traditional network deployment
approach. The group’s ultimate goal is to help provide better connectivity for
communities all over the world as more people come on-line and demand more
bandwidth- intensive experiences like video, virtual reality and augmented
reality.

Within TIP, the Open Optical Packet Transport (OOPT) project group is chartered
with unbundling monolithic packet-optical network technologies in order to
unlock innovation and support new, more flexible connectivity paradigms.

The key to unbundling is the ability to accurately plan and predict the
performance of optical line systems based on an accurate simulation of optical
parameters. Under that OOPT umbrella, the Physical Simulation Environment (PSE)
working group set out to disrupt the planning landscape by providing an open
source simulation model which can be used freely across multiple vendor
implementations.

.. |docs| image:: https://readthedocs.org/projects/gnpy/badge/?version=develop
  :target: http://gnpy.readthedocs.io/en/develop/?badge=develop
  :alt: Documentation Status
  :scale: 100%

.. |build| image:: https://travis-ci.org/mcantono/gnpy.svg?branch=develop
  :target: https://travis-ci.org/mcantono/gnpy
  :alt: Build Status
  :scale: 100%

TIP OOPT/PSE & PSE WG Charter
-----------------------------

We believe that openly sharing ideas, specifications, and other intellectual
property is the key to maximizing innovation and reducing complexity

TIP OOPT/PSE's goal is to build an end-to-end simulation environment which
defines the network models of the optical device transfer functions and their
parameters.  This environment will provide validation of the optical
performance requirements for the TIP OLS building blocks.

- The model may be approximate or complete depending on the network complexity.
  Each model shall be validated against the proposed network scenario.
- The environment must be able to process network models from multiple vendors,
  and also allow users to pick any implementation in an open source framework.
- The PSE will influence and benefit from the innovation of the DTC, API, and
  OLS working groups.
- The PSE represents a step along the journey towards multi-layer optimization.

License
-------

``gnpy`` is distributed under a standard BSD 3-Clause License.

See `LICENSE <LICENSE>`_ for more details.



