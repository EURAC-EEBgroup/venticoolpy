# Overview

The _VentiCoolPy_ is intended as a preliminary assessment resource to support early-stage design decisions related to passive cooling strategies. While the method provides valuable insights into the potential of ventilative cooling under typical conditions, it is essential to acknowledge its inherent limitations.


This library relies on simplified assumptions, including the use of uniform air temperature and the omission of complex thermal dynamics. As such, it is not suitable for detailed analyses in spaces where:

- Thermal stratification, solar gain patterns, or heat storage effects play a significant role;
- The architecture is complex, such as multi-zone or multi-story buildings;
- Large glazed surfaces or dynamic solar exposure significantly influence thermal performance;
- Thermal bridges, non-uniform solar radiation, or advanced material interactions must be accurately accounted for.

In these contexts, the use of more comprehensive dynamic simulation tools is strongly recommended. As building design progresses and more detailed information becomes available, transitioning to advanced modeling platforms ensures greater accuracy, more reliable predictions, and the development of an optimized ventilative cooling strategy.
By using this library, users acknowledge that results are indicative and should be validated with detailed simulations before informing final design decisions or implementation strategies.

The ventilative cooling potential analysis is based on a methodology developed within International Energy Agency (IEA) Annex 62 project with the aim to assess in the early design stages the potential effectiveness of ventilative cooling strategies by taking into account also building envelope thermal properties, occupancy patterns, internal gains and ventilation needs.

The methodology and corresponding spreadsheet tool has been further developed by using relevant equations, including thermal mass, and methods from EN ISO 52016-1:2017 for energy balance calculation. The calculation methodology is integrated in Annex G of the technical specifications " Ventilation for buildings — Ventilative cooling systems — Design” – currently in preparation.