From EN ISO 52016-1, but stripped from the subscripts for different thermal zones (ztc) and stripped from the subscripts for different (transmission or ventilation) elements (k) and stripped from the indication of the source of input data:
𝐻𝑡𝑟 overall heat transfer coefficient by transmission (W/K);
𝑞𝑉;𝑡 airflow rate (m3/s);
𝜌𝑎 ∙ 𝑐𝑎 heat capacity of air per volume (J/(m3K) = 1,204 x 1 006);
𝐻𝑣𝑒;𝑡 overall heat exchange coefficient by ventilation (W/K);
𝜃𝑖𝑛𝑡;𝑡 internal air or operative temperature at time interval t (°C);
NOTE: for the 1RC model there is no distinction between air and operative
temperature.
𝜃𝑖𝑛𝑡;𝑡− internal temperature at previous time interval (t-Δt) (°C);
𝜃𝑖𝑛𝑡;𝑠𝑒𝑡;𝐻;𝑡 internal operative temperature setpoint for heating at time interval t;
NOTE Setpoint can vary in time, e.g. if the adaptive comfort model is applicable (see EN
16798-1:2019 [9]).
𝜃𝑖𝑛𝑡;𝑠𝑒𝑡;𝐶;𝑡 internal operative temperature setpoint for cooling at time interval t;
NOTE Setpoint can vary in time, e.g. if the adaptive comfort model is applicable (see EN
16798-1:2019 [9]).
𝜃𝑒;𝑎;𝑡 external air temperature at time interval t (°C);
𝛷𝑖𝑛𝑡;𝑡 total internal heat gain at time interval t (W);
𝛷𝑠𝑜𝑙;𝑡 total solar heat gain at time interval t (W)
𝛷𝐻𝐶;𝑡 heating load (if positive) or cooling load (if negative) at time interval t (W);
𝐶𝑖𝑛𝑡 (lumped) internal thermal capacity (J/K);
NOTE The methodology considers the simplified lumped capacity, covering internal
capacity in the building and weighted capacity of the constructions.
𝛥𝑡 length of the time interval t (s, in casu: 3600 s).

The following parameters have been added to calculate the ventilative cooling potential:
𝑞𝑉;𝑚𝑖𝑛 minimum required airflow rate for hygienic ventilation (m3/s);
𝑞𝑚;𝑡 air mass flow rate (kg/s);
𝐴𝐶𝐻𝑡 volumetric air change per hour (1/h)
𝑞𝑉;𝑉𝐶𝑆;𝑟𝑒𝑞;𝑡 required airflow rate for ventilative cooling (m3/s);
𝛥𝜃𝑐𝑟𝑖𝑡 minimum temperature difference between indoor and outdoor temperature in order to drive natural airflow and/or in order to have a more than negligible cooling potential (K, i.e. 3K);
𝛷𝐻𝑈;𝑒;𝑎;𝑡 relative humidity of outdoor air (%);
NOTE EN ISO 52016-1 uses absolute humidity as input variable.
𝛷𝐻𝑈;𝑚𝑎𝑥 maximum relative humidity of outdoor air for ventilative cooling (%, i.e. 85%);
𝜃𝑖𝑛𝑡;𝑐𝑜𝑚𝑓𝑜𝑟𝑡;𝑡 indoor comfort temperature according to adaptive comfort model of EN 16798-1:2019 (°C).
The energy balance for the single zone at timestep t can be written as (Formula (H.6)):
[𝐶𝑖𝑛𝑡∆𝑡 + 𝐻𝑣𝑒;𝑡 + 𝐻𝑡𝑟] 𝜃𝑖𝑛𝑡;𝑡 = 𝐶𝑖𝑛𝑡∆𝑡 𝜃𝑖𝑛𝑡;𝑡−1 + [𝐻𝑣𝑒;𝑡 + 𝐻𝑡𝑟] 𝜃𝑒;𝑎;𝑡 + 𝛷𝑖𝑛𝑡;𝑡 + 𝛷𝑠𝑜𝑙;𝑡 + 𝛷𝐻𝐶;𝑡 (H.6)
with the overall heat exchange coefficient by ventilation, expressed in W/K, defined as follow:
𝐻𝑣𝑒;𝑡 = 𝜌𝑎 𝑐𝑎 𝑞𝑉;𝑡 (H.7)
and the airflow rate, expressed in m3/s, equal to:
𝑞𝑉;𝑡 = 𝑚̇ 𝜌𝑎 𝐴𝑓

where
𝜌𝑎 density of air (kg/m3), assumed equal to 1,204 kg/m3
𝑐𝑎 specific heat of air (J/kg K), assumed equal to 1 006 J/kg K
𝑚̇ mass flow rate of air (kg/s m2)
𝐴𝑓 floor area (m2)
Since the unknown terms are either the node air temperature or the heating/cooling loads, the equation can be rewritten as:
𝐴 𝜃𝑖𝑛𝑡;𝑡 = 𝐵 + 𝛷𝐻𝐶;𝑡 
With A and B known at each time interval t.
In the next sections are shown the steps to assess the potential of the methodology.