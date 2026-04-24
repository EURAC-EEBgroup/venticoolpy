<!-- markdownlint-disable MD041 -->
# Welcome to VentiCoolPy

![VentiCoolPy Logo](https://raw.githubusercontent.com/EURAC-EEBgroup/venticoolpy/main/docs/media/venticoolpy_logo.png) <!-- markdownlint-disable-line MD041 -->


[![PyPI version](https://badge.fury.io/py/venticoolpy.svg)](https://badge.fury.io/py/venticoolpy)
[![Documentation status](https://github.com/EURAC-EEBgroup/venticoolpy/actions/workflows/docs.yml/badge.svg)](https://github.com/EURAC-EEBgroup/venticoolpy/actions/workflows/docs.yml)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)


**VentiCoolPy** is a Python library developed by Eurac Research to support the development of sustainable cooling strategies for buildings.
This Python library provides the reference implementation of the ventilative cooling potential method developed by the Eurac Research within IEA/EBC Annex 62 and subsequently integrated into the prCEN/TS “Ventilative cooling systems – Design”.
It operationalises the standardised methodology into an open and extensible computational tool for research and professional applications.

The ventilative cooling potential method aims at assessing the cooling potential of ventilative cooling (fx. using natural forces) in a reference thermal and ventilation zone representing the building in its context. 

The ventilative cooling potential method provides a practical approach for application during the early stages of building design, such as the feasibility stage. It enables preliminary evaluation in the absence of detailed system specifications and leverages the adaptive comfort model to account for occupants' ability to adapt to varying indoor conditions, offering a realistic assessment of comfort levels.

## Key Features

- early-stage design applicability
- climate and building-dependent assessment
- single-zone hourly simulation of thermal balance
- explicit consideration of building thermal inertia
- frequency analysis of required ventilation rates to maintain thermal comfort over the full year
- use of adaptive thermal comfort model


 

## Installation

To get started with _VentiCoolPy_, you'll need to install it first. You can do this by running the following command:

```bash
pip install venticoolpy
```

## Documentation
This [documentation](overview/index.md) is designed to help you understand and use VentiCoolPy effectively.

### Tutorials
Practical examples showing how to use our project in real-world scenarios. For more information, please see the [Tutorials](tutorials.md) section.


## Web Application

A web app is available to use the library directly through an interface at the following [link](https://tools.eeb.eurac.edu/vctlib/).

## License

VentiCoolPy is licensed under the BSD 3-Clause License. For more information, please see the [LICENSE](https://github.com/EURAC-EEBgroup/venticoolpy/blob/main/LICENSE) file.

## Contact

For any questions or support, please contact:

**Concept and Methodology**

- Annamaria Belleri <annamaria.belleri@eurac.edu>

**Python Code and Web Tool**

- Olga Somova <olga.somova@eurac.edu>

**other contributors**
- Ali Sana Fatima <sanafatima.ali@eurac.edu> (vertical irradiance code)
- Valentina Radice Fossati (validation of the calculation methdology)
- Dick Van Djik  <dick.vandijk@epb.center> (thermal balance calculation method)

## Contributing

Please feel free to contact us with any potential suggestions, avenues for collaboration, etc.


## Citation 

Please cite us if you use the _VentiCoolPy_ library:

    Fossati V., Belleri A., Van Djik D., A methodology for evaluating the ventilative cooling potential in early-stage building design, AIVC 2023 conference proceedings, Copenhagen, October 2023

## Acknowledgements
This work has received funding from the European Union's Horizon Europe research and innovation programme under grant agreement No 101138672 (HeriTACE).
The calculation methodology implemented in this library has been adopted by CEN/TC 156/WG21 and included in their technical specification on ventilative cooling systems. We gratefully acknowledge the WG21 experts for their feedback.