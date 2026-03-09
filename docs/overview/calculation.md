## 1. Pre-calculation procedure

### 1.1 Outdoor running mean temperature and adaptive comfort limits
The outdoor running mean temperature and adaptive comfort limits at each timestep is calculated in accordance with EN 16798-1:2019. Adaptive comfort limits are calculated according to the comfort category defined by the user.
In case of data absence refer to Table B.5 of EN 16798-1:2019.

### 1.2 Solar radiation calculation
Beam irradiance and total irradiance over each fenestration orientations (E, N, NE, NW, S, SE, SW, W) for each
hour of the time series is calculated using weather file metadata from the .epw file header (latitude, longitude, altitude, and time zone) and Perez sky model within the pvlib python library.

The total irradiance over the glazed surface is given by the sum of beam and diffuse radiation for each window of the room according to this equation:

$𝐼_{𝑡𝑜𝑡,𝑖} = 𝐼_{𝑏,𝑖} + 𝐼_𝑑$

where

𝑖 refers to the window orientations (E, N, NE, NW, S, SE, SW, W)

$𝐼_{𝑡𝑜𝑡}$ total solar irradiance for each window (W/m²)

$𝐼_{𝑏,𝑖}$ beam irradiance(W/m²)

$𝐼_𝑑$ diffuse solar irradiance (W/m²)

NOTE In EN ISO 52016-1:2018 solar gains are split into direct (into the zone, through the windows) and
indirect (absorbed in external constructions). In the underlying methodology it is just the total. The effect of
movable solar shading provisions is considered on an hourly basis.

### 1.3 Internal gains calculation
Hourly solar heat gains, expressed in W/m2, are calculated using the equation:

$\phi_{𝑠𝑜𝑙} = 𝐼_{𝑡𝑜𝑡,𝑖} \cdot 𝑔 \cdot 𝑌 \cdot \frac{𝐴_w} {𝐴_𝑓}$


where

𝑔 g-value of the glazing system (-) 

𝑌 shading factor (-)

$𝐴_𝑤$ area of the window (m²)

$𝐴_𝑓$ floor area (m²)

Data related to the room geometry and technical specifications of the transparent envelope are defined by the user. Shading factor is a user input only if the total irradiance for each orientation is greater than the shading control setpoint, else is equal to 1. The shading control setpoint input should be provided by the user as well.

𝑌 = user input if $𝐼_{𝑡𝑜𝑡,𝑖} > 𝑆ℎ𝑑$, 𝑒𝑙𝑠𝑒 𝑌 = 1 

Although in EN ISO 52016-1 the solar gains are split into direct and indirect, respectively into the zone, through the windows, and absorbed in external constructions, the methodology considers just the total.
Internal heat gains are expressed in W/m² and are calculated for each hour of a time series by means of the equation:

$\phi_{𝑖𝑛𝑡} = {𝑝𝑒𝑜𝑝𝑙𝑒} \cdot 𝑜𝑐c_{sch} \cdot \frac {𝑞_{𝑜𝑐c}} {A_f} + 𝑞_𝐿 \cdot 𝑙𝑔𝑡_{𝑠𝑐ℎ} + 𝑞_𝐴 \cdot 𝑎𝑝𝑙_{𝑠𝑐ℎ}$ 

where

𝑝𝑒𝑜𝑝𝑙𝑒 = maximum number of people in the reference room

$𝑜𝑐c_{sch}$ hourly occupancy schedule (-)

$𝑞_{𝑜𝑐c}$ internal heat gains per person depending on their degree of activity (W)

$𝑞_𝐿$ lighting power density (W/m²)

$𝑙𝑔𝑡_{𝑠𝑐ℎ}$ hourly lighting schedule (-)

$𝑞_𝐴$ electric equipment power density (W/m²)

$𝑎𝑝𝑙_{𝑠𝑐ℎ}$ hourly electric equipment schedule (-)

The ventilative cooling potential method uses the hourly schedules as reference reported in EN 16798-1:2019 (Annex C). Default schedules are indicated for each building typology.

### 1.4 Overall heat transfer coefficient by transmission
The overall heat transfer coefficient by transmission through the opaque and transparent envelope, expressed in W/K, is computed as follows:

$𝐻_{𝑡𝑟} = ∑ 𝑈_{𝑎𝑣𝑔} \cdot 𝐴_𝑒 = ∑ \frac {𝑈_{𝑜𝑝}(𝐴_𝑒 − 𝐴_𝑤) + 𝑈_𝑤 \cdot 𝐴_𝑤}{A_e} \cdot 𝐴_e$

where:

$𝑈_{avg}$ average thermal transmittance of the envelope (W/m²K)

$𝐴_𝑒$ area of the envelope (m²)

$𝐴_𝑤$ area of the transparent envelope (m²)

$𝑈_𝑜$ thermal transmittance of the opaque envelope (W/m²K)

$𝑈_𝑤$ thermal transmittance of the transparent envelope (W/m²K)

### 1.5 Internal thermal capacity calculation
According to EN ISO 52016-1, for the application of the hourly calculation, each construction of the building envelope has its own heating capacity. For the early feasibility stage, using the overall heat transfer coefficient, a simplified approach is needed, more similar to the monthly calculation method of EN ISO 52016-1.
The internal thermal capacity of the entire thermal zone corresponds to the weighted sum of the thermal masses due to building envelope, air and furniture. The specific heat capacity of air and furniture is considered: 
$𝑘_{𝑚;𝑖𝑛𝑡}$ = 10 000 J/(m²K)


## 2. Thermal balance calculations

### 2.1 Definitions of keys in formulas
From EN ISO 52016-1, but stripped from the subscripts for different (transmission or ventilation) elements and stripped from the indication of the source of input data:

$𝐻_{𝑡𝑟}$ overall heat transfer coefficient by transmission (W/K);

$q_{V;t}$ airflow rate ($m^3/s$);

$𝜌_𝑎 \cdot 𝑐_𝑎$ heat capacity of air per volume $J/(m^3K)$;

$𝐻_{𝑣𝑒;𝑡}$ overall heat exchange coefficient by ventilation (W/K);

$\theta_{𝑖𝑛𝑡;𝑡}$ internal air or operative temperature at time interval t (°C);
NOTE: for the 1RC model there is no distinction between air and operative
temperature.

$\theta_{𝑖𝑛𝑡;t−Δt}$ internal temperature at previous time interval (t-Δt) (°C);

$\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$ internal operative temperature setpoint for heating at time interval t;
NOTE Setpoint can vary in time, e.g. if the adaptive comfort model is applicable (see EN
16798-1:2019).

$\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;C;𝑡}$ internal operative temperature setpoint for cooling at time interval t;
NOTE Setpoint can vary in time, e.g. if the adaptive comfort model is applicable (see EN
16798-1:2019).

$\theta_{𝑒;𝑎;𝑡}$ external air temperature at time interval t (°C);

$\Phi_{𝑖𝑛𝑡;𝑡}$ total internal heat gain at time interval t (W);

$\Phi_{𝑠𝑜𝑙;𝑡}$ total solar heat gain at time interval t (W)

$\Phi_{HC;𝑡}$ heating load (if positive) or cooling load (if negative) at time interval t (W);

$𝐶_{𝑖𝑛𝑡}$ (lumped) internal thermal capacity (J/K);
NOTE The methodology considers the simplified lumped capacity, covering internal
capacity in the building and weighted capacity of the constructions.

𝛥𝑡 length of the time interval t (s, in casu: 3600 s).

The following parameters have been added to calculate the ventilative cooling potential:

$𝑞_{𝑉;𝑚𝑖𝑛}$ minimum required airflow rate for hygienic ventilation ($m^3/s$);

$𝑞_{𝑚;𝑡}$ air mass flow rate (kg/s);

$𝐴𝐶𝐻_𝑡$ volumetric air change per hour (1/h)

$𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$ required airflow rate for ventilative cooling ($m^3/s$);

$𝛥𝜃_{𝑐𝑟𝑖𝑡}$ minimum temperature difference between indoor and outdoor temperature in order to drive natural airflow and/or in order to have a more than negligible cooling potential (K, i.e. 3K);

$𝛷_{𝐻𝑈;𝑒;𝑎;𝑡}$ relative humidity of outdoor air (%);
NOTE EN ISO 52016-1 uses absolute humidity as input variable.

$𝛷_{𝐻𝑈;𝑚𝑎𝑥}$ maximum relative humidity of outdoor air for ventilative cooling (%, i.e. 85%);

$\theta_{𝑖𝑛𝑡;𝑐𝑜𝑚𝑓𝑜𝑟𝑡;𝑡}$ indoor comfort temperature according to adaptive comfort model of EN 16798-1:2019 (°C).

The energy balance for the single zone at timestep t can be written as:
$$ \bigl(C_{int}/\Delta t + H_{ve,t} + H_{tr}\bigr)\,\theta_{int,t} = C_{int}/\Delta t\, \theta_{int,t-1} + (H_{ve,t} + H_{tr})\,\theta_{e,a,t} + \Phi_{int,t} + \Phi_{sol,t} + \Phi_{HC,t} $$ 

where: 

- $\theta_{int,t}$: indoor air temperature  
- $\theta_{e,a,t}$: outdoor air temperature  
- $\Phi_{HC,t}$: heating/cooling load

with the overall heat exchange coefficient by ventilation, expressed in W/K, defined as follow:

$𝐻_{𝑣𝑒;𝑡} = 𝜌_𝑎 \cdot 𝑐_𝑎 \cdot 𝑞_{𝑉;𝑡}$ 

and the airflow rate, expressed in $m^3/s$, equal to:

$𝑞_{𝑉;𝑡} = 𝑚̇ \cdot 𝜌_𝑎 \cdot 𝐴_𝑓$

where

$𝜌_𝑎$ density of air ($kg/m^3$), assumed equal to 1,204 ($kg/m^3$)

$𝑐_𝑎$ specific heat of air (J/kg-K), assumed equal to 1 006 J/kg-K

𝑚̇ mass flow rate of air ($kg/s-m^2$)

$𝐴_𝑓$ floor area ($m^2$)

Since the unknown terms are either the node air temperature or the heating/cooling loads, the equation can be rewritten as:

$𝐴 \cdot $\theta_{𝑖𝑛𝑡;𝑡}$ = 𝐵 + $\Phi_{HC;𝑡}$ 

with A and B known at each time interval t.

In the next sections are shown the steps to assess the potential of ventilative cooling.

### 2.2 Calculation of time series in free float temperature mode
The first case serves for validation purposes. At each time interval, $𝐴_𝑡$ and $𝐵_𝑡$ without ventilative cooling are calculated.

NOTE $𝐵_𝑡$ is a function of the indoor temperature calculated during the previous time interval $\theta_{𝑖𝑛𝑡;t−Δt}$.

NOTE $𝐴_𝑡$ will be constant if the ventilation rate is constant.

The ventilation rate is assumed to be the minimum ventilation rate: 

$𝑞_{𝑉;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛}$

$\theta_{𝑖𝑛𝑡;0,𝑡} = 𝐵_𝑡 \cdot A_𝑡$

Since there is no heating or cooling: 

$\theta_{𝑖𝑛𝑡;𝑡} = \theta_{𝑖𝑛𝑡;0,𝑡}$

The calculation is repeated for the successive time intervals until the end of the year. An initialization period of a month is used to avoid the influence of assumed indoor temperature at the beginning of the calculation that can have an impact on the results over a high number of time intervals.

### 2.3 Calculation of time series with heating and cooling needs without ventilative cooling
This case serves as the reference case for the comparison against the case with ventilative cooling. Regardless of the way, in early feasibility stage the goal is to estimate the amount of heating and cooling load that needs to be satisfied at each hour. Therefore, there is no upper limit to the heating or cooling capacity.
This implies that the indoor temperature will never drop below the heating setpoint nor exceed the higher cooling setpoint for a given time interval. This allows for a straightforward calculation in just a few steps:

— Step 1: Calculation of the indoor temperature without heating or cooling and without ventilative cooling (same formulae as in [section 2.2](#22-calculation-of-time-series-in-free-float-temperature-mode))

— Step 2: Calculation of heating or cooling load and actual indoor temperature, without ventilative
cooling.

If $\theta_{𝑖𝑛𝑡;0,𝑡} < \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$, 

then: HEATING LOAD

$\Phi_{𝐻𝐶;𝑡} = \Phi_{𝐻;𝑡} = 𝐴_𝑡 \cdot \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡} − 𝐵_𝑡$

and $\theta_{𝑖𝑛𝑡;𝑡} = \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$


If $\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡} ≤ \theta_{𝑖𝑛𝑡;0;𝑡} ≤ \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$, 

then: NO HEATING or COOLING LOAD

$\Phi_{𝐻𝐶;𝑡} = 0$

If $\theta_{𝑖𝑛𝑡;0,𝑡} > \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$, 

then: COOLING LOAD

$\Phi_{𝐻𝐶;𝑡} = \Phi_{C;𝑡}  = 𝐴_𝑡 \cdot \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡} − 𝐵_𝑡$

NOTE Negative value.

$\theta_{𝑖𝑛𝑡;𝑡} = 𝐵_𝑡 + \Phi_{𝐻𝐶;𝑡} \cdot 𝐴_𝑡$  

NOTE

In case of no heating or cooling load: $\theta_{int;t} = \theta_{𝑖𝑛𝑡;0,𝑡}$

In case of heating load: $\theta_{int;t} = \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$

In case of cooling load: $\theta_{int;t} = \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;C;𝑡}$ 

Step 1 and Step 2 are repeated for the successive time intervals until the end of the year. Even in this case, an initialization period to avoid influence of assumed indoor temperature at the start of the calculation is used.

### 2.4 Calculation of time series with heating and cooling needs and ventilative cooling
This case considers the ventilative cooling potential capacity and is compared against the previous case without ventilative cooling.

For the same reasons indicated previously, even in this case there is no upper limit to the heating or cooling capacity. For similar reasons there is also no limit to the required air flow rate to satisfy the cooling needs by ventilative cooling. 

— Step 1: Calculation of the indoor temperature without heating or cooling (same formulae as in [section 2.2](#22-calculation-of-time-series-in-free-float-temperature-mode)).

— Step 2: Calculation of heating or cooling load and actual indoor temperature, without ventilative
cooling (same formulae as in [section 2.3](#23-calculation-of-time-series-with-heating-and-cooling-needs-without-ventilative-cooling)).

— Step 3: Calculation of the heating or cooling load and actual indoor temperature, with ventilative
cooling.

Ventilative cooling mode (VC-mode) is determined according to the evaluation criteria described in [section 3](#3-evaluation-criteria-for-ventilative-cooling-potential).

If [VC-mode ≠ #2]:
If there is a cooling load, it is not covered by ventilative cooling but by whatever other provision (active cooling).

NOTE The calculation results from Step 2 for this time interval remain valid. Despite that, it is better to simply assess the increased or not increased ventilation rate and recalculate the heating and cooling loads with this input and internal temperature as shown in Step 4. 

Ventilation rate is assumed to be the minimum one:

$𝑞_{𝑉;𝑉𝐶𝑆;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛}$

If [VC-mode = #1] the ventilation rate is not increased but the existing (minimum) ventilation will be counted as part of ventilative cooling.

If [VC-mode = #2] the ventilation rate for ventilative cooling is increased. The increased ventilation rate can be assessed as follows:

The formulae for $𝐴_𝑡$ and $𝐵_𝑡$ is rewritten.

$𝐴_{VCS;𝑡} = 𝐴_𝑡 + ∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$ 

$𝐵_{VCS;𝑡} = 𝐵_𝑡 + ∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡} \cdot \theta_{𝑒;𝑎;𝑡}$

In which 

$∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$ is the increase of the overall heat exchange coefficient due to the extra ventilation rate.

$∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡} = 𝜌_𝑎 \cdot 𝑐_𝑎 \cdot 𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$

The required extra ventilation rate needed to supply ventilative cooling ($𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}) can be assessed assuming that all cooling power is provided by extra ventilation. As a consequence, cooling loads are assumed to be null. The procedure to determine the value of $𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$ is explained below.

At each time interval, if VC-mode = #2:

$(𝐴_𝑡 + ∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}) \cdot \theta_{𝑖𝑛𝑡;𝑡} = 𝐵_𝑡 + ∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡} \cdot \theta_{𝑒;𝑎;𝑡}$

Therefore,

$∆𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡} = \frac{𝐵_𝑡 − 𝐴_𝑡 \cdot \theta_{𝑖𝑛𝑡;𝑡}}{\theta_{𝑖𝑛𝑡;𝑡} − \theta_{𝑒;𝑎 𝑡}}$

The internal temperature $\theta_{𝑖𝑛𝑡;𝑡}$ of the equation coincides with the cooling setpoint.

Then, the required extra ventilation for ventilative cooling is equal to:

$∆𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡} = \frac{𝐵_𝑡 − 𝐴_𝑡 \cdot \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}} {𝜌_𝑎 \cdot 𝑐_𝑎 \cdot (\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡} − \theta_{𝑒;𝑎;𝑡})}$

with $\theta_{𝑖𝑛𝑡;𝑡} = \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$.

The ventilation rate necessary to provide ventilative cooling is given by the sum of the minimum required ventilation rates and the extra ventilation required.

$𝑞_{𝑉;𝑉𝐶𝑆;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛} + ∆𝑞_{𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡}$ 

— Step 4: Recalculation of heating or cooling load and internal temperature with the actual ventilation rate.

$𝐴_{𝑉𝐶𝑆}$ and $𝐵_{𝑉𝐶𝑆}$ with the actual value (= value depending on the VC-mode) for $𝐻_{𝑣𝑒;𝑉𝐶𝑆;𝑡}$ should be calculated.

If $\theta_{𝑖𝑛𝑡;0;𝑡} < \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$, then: HEATING LOAD

$\Phi_{𝐻𝐶;𝑉𝐶𝑆;𝑡} = \Phi_{𝐻;𝑉𝐶𝑆;𝑡} = 𝐴_{𝑉𝐶𝑆;𝑡} \cdot \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡} − 𝐵_{𝑉𝐶𝑆;𝑡}$ 

If $\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡} ≤ \theta_{𝑖𝑛𝑡;0;𝑡} ≤ \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$, then: NO HEATING or COOLING LOAD

$\Phi_{𝐻𝐶;𝑉𝐶𝑆;𝑡} = 0$

If $\theta_{𝑖𝑛𝑡;0;𝑡} > \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$, then: COOLING LOAD

$\Phi_{𝐻𝐶;𝑉𝐶𝑆;𝑡} = \Phi_{𝐶;𝑉𝐶𝑆;𝑡} = 𝐴_{𝑉𝐶𝑆;𝑡} \cdot \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡} − 𝐵_{𝑉𝐶𝑆;𝑡}$

NOTE Negative value

Calculation of the indoor temperature:

$\theta_{𝑖𝑛𝑡;𝑡} = 𝐵_{𝑉𝐶𝑆;𝑡} + \Phi_{𝐻𝐶;𝑉𝐶𝑆;𝑡} \cdot 𝐴_{𝑉𝐶𝑆;𝑡}$ 

Step 1, Step 2, Step 3 and Step 4 should be repeated for the successive time intervals until the end of the year. An initialization period of a month is used to avoid influence of assumed indoor temperature at the start of the calculation.

## 3. Evaluation criteria for ventilative cooling potential

For each hour of the annual climatic record of the given location, the energy balance is calculated according to the model above and an algorithm splits the total number of hours when the building is occupied into four groups:

1) Ventilative cooling mode #0, ventilative cooling not required;

2) Ventilative cooling mode #1, direct ventilative cooling with minimum airflow rates;

3) Ventilative cooling mode #2, direct ventilative cooling with increased airflow rates;

4) Ventilative cooling mode #3, direct ventilative cooling cannot provide benefits.

NOTE The calculation focuses mainly on direct ventilative cooling. By direct ventilative cooling is meant the use of natural ventilative cooling to ensure indoor air quality as well as thermal comfort.

**Ventilative cooling mode #0 – ventilative cooling not required**

Ventilative cooling is not required during occupied hours in which indoor temperature is below the lower comfort zone limit (heating is needed).

If $\theta_{𝑖𝑛𝑡;0;𝑡} < \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡}$

then $𝑞_{𝑉;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛}$ (with heat recovery)

in VC-mode #0 $𝑞_{𝑉;𝑡}$ is not counted as part of the ventilative cooling potential.

**Ventilative cooling mode #1 – direct ventilative cooling with minimum airflow rates**

This mode considers that direct ventilation with airflow rate maintained at the minimum required for indoor air quality can potentially ensure comfort when the outdoor temperature is within the comfort ranges.

If $\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡} ≤ \theta_{𝑖𝑛𝑡;0;𝑡} ≤ \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$

then $𝑞_{𝑉;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛}$ (no heat recovery needed)

Unlike the previous case, $𝑞_{𝑉,𝑡}$ is counted as part of the ventilative cooling potential.

**Ventilative cooling mode #2 – direct ventilative cooling with increased airflow rates**

Direct ventilative cooling with increased airflow rate can potentially ensure thermal comfort and indoor air quality in the air node.

If $\theta_{𝑖𝑛𝑡;0;𝑡} > \theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡}$,

$\theta_{𝑒;𝑎;𝑡} ≤ (\theta_{𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡} − ∆𝜃_{𝑐𝑟𝑖𝑡})$, and

$\phi_{𝐻𝑈;𝑒;𝑎;𝑡} < \phi_{𝐻𝑈;max}$ 

Then $𝑞_{𝑉;𝑡} = 𝑞_{𝑉;𝑉𝐶𝑆}$

Obviously, in VC-mode #2 𝑞𝑉,𝑡 is counted as part of the ventilative cooling potential.

NOTE In a less conservative approach the potential for ventilative cooling could also apply to hours in which the outdoor air temperature is higher than the cooling setpoint, if the indoor temperature without cooling is a few degrees higher than this air outdoor temperature.
Once the actual ventilation rate has been calculated according to VC-mode, heating or cooling loads and the internal temperature are calculated again, before proceeding with the next time step.

**Ventilative cooling mode #3 – direct ventilative cooling cannot provide benefits**

The last mode refers to all other situations: the case in which direct ventilative cooling cannot provide benefits because the outdoor temperature exceeds to the upper limits of the comfort zone, or the outdoor air is too humid.

$𝑞_{𝑉;𝑡} = 𝑞_{𝑉;𝑚𝑖𝑛}$
