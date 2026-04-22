
### Building input data 

The VC tool performs calculations on a reference thermal and ventilation zone within the building. The selected zone should be carefully chosen to be representative of the buildings characteristics, exposure and typical use. 

NOTE: If needed, the calculation can be repeated for additional zones within the building to capture variations in usage patterns, construction features, or exposure. 




####**Required inputs**  

Once the reference zone has been defined, the following inputs are required:

- Building type (a value equal to: 'Apartment building', 'Daycare center', 'Detached house', 'Hospital', 'Hotel', 'Office', 'Restaurant', 'School'; required): select the type of building choosing among the listed categories 

- Ceiling to floor height; H (m).: input the net room height (internal ceiling to floor height) in m to calculate net room air volume 

- Envelope area; $A_e$ (m²): Gross envelope area (incl. both opaque and glazed area) which has outside temperature as boundary condition (excl. interior walls, floors and ceilings). This area, multiplied by the average thermal transmittance, is used to estimate the transmission. 

- Floor area ; $A_f$ (m²): The net floor area of the room to calculate net room air volume $V = H \cdot A_f$ and internal gains. 

- Fenestration area; $A_g$ (m²): Total window area (incl. frame). If more windows are present in the reference room please insert the sum area. 

- Comfort requirements (a value equal to: 'category I', 'category II', 'category III'): 
Comfort requirements refer to the comfort categories defined by the EN 16798-1: 2019 standard. Recommended input values given for each of the different comfort categories are included in the tool and automatically selected.  

- Maximum relative humidity accepted; $RH_{max}$ (%): enter the max. outdoor relative humidity of outdoor air accepted for ventilative cooling (i.e. 85%). If the outdoor relative humidity of the weather file exceeds this value, direct ventilative cooling cannot provide benefits because the outdoor air is considered too humid. 

- U-value of the opaque envelope; $U_o$ (W/m²K): Average thermal transmittance of the opaque surfaces (wall, roof, floor) with outdoor boundary conditions.  

- U-value of the fenestration; $U_w$ (W/m²K): Thermal transmittance of the window (or average thermal transmittance of windows if the room has more than one window), considering both glazing system and frame.  

- Construction mass; $C_{int}$ (J/m²K): select predefined specific heat capacity of the construction. very light= 50000 J/m²K, light= 75000 J/m²K, medium = 110000 J/m²K, heavy = 175000 J/m²K,  and very heavy = 250000 J/m²K. NOTE: different values can be input in the optional input session. In case a value different than .1 for the (lumped) internal thermal capacity Cint (J/K) is entered for the construction mass in the optional input session, this input is ignored. 

- g value of the glazing system; g (-): Solar heat gain coefficient of the window glazing system.  

- fenestration orientation (a value equal to: N, NE, E, SE, S, SW, W, NW): Fenestration orientation is the direction the window faces, expressed relative to the cardinal directions; for example, a north‑oriented window is a window that faces north and the user shall select N as the fenestration orientation.

- Shading control setpoint; Shd (W/m²): Shading is on if the specific beam plus diffuse solar radiation incident on the window exceeds this setpoint value (generally is between 40 and 150 W/m²).  

- Shading factor; Y (-): Parameter indicating the presence of an external shading element and the surface of the window which is shaded by the shading element (i.e. shutter, venetian blinds, roll up blinds..). Y = 1 means all the surface is completely shaded, Y = 0 means that there is no shading element. 

- Time control on; $t_{on}$; min 0, max 24. Time control off; $t_{off}$; min 0, max 24: Parameter indicating the presence of the occupant within the thermal zone.  NOTE	if the building is occupied all day long (24/24) enter zero as time control on and 24 as time control off.  

####**Optional inputs**  
A set of optional inputs can be entered to customize default input values:

- Minimum required ventilation rates: ventilation rates required to maintain an acceptable indoor air quality. If not specified this valued is calculated according to IEQ standard (EN 16798-1:2019) design requirements for indoor air quality. The value can be input in any of the following unit of measure: '1/h', 'kg/s-m²', 'm³/h', 'm³/s', 'l/s-m²'. Please select the unit of measure corresponding to the input value from the list. Please note that to select a unit of measure, it is necessary to first deselect any other active selections. 

- Lighting power density; $Q_{el_lgt}$ (W/m²): The maximum lighting level per floor area. Internal gains due to lighting are calculated by multiplying the lighting power by the pre-defined load profiles.  

- Electric equipment power density; $Q_{el_equip}$ (W/m²): The maximum electric equipment level per floor area. Internal gains due to electric equipment are calculated by multiplying the electric equipment power density by the pre-defined load profiles.  

- Occupancy density; $Q_{people}$ (people/m²): The maximum number of person per floor area. Internal gains due to people are calculated by multiplying the maximum number of person by the pre-defined occupancy profiles.  

- Internal thermal capacity; $C_{int}$ (J/K): The (lumped) internal thermal capacity of the entire thermal zone corresponds to the weighted sum of the thermal masses due to building envelope, air and furniture.  
