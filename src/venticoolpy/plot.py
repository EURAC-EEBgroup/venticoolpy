import calendar
try:
    import altair as alt
    from IPython.display import display as _display
except ImportError as e:
    raise ImportError(
        "Plot features require extra dependencies. Install with: pip install 'venticoolpy[plot]'"
    ) from e



def _in_notebook() -> bool:
    try:
        from IPython import get_ipython  # type: ignore
        ip = get_ipython()
        return ip is not None and "IPKernelApp" in ip.config
    except Exception:
        return False



def plot_vent_mode_over_year(df_vent_mode, display="auto", save=False, fp=None):
    """
    Create and (optionally) display/save a stacked Altair chart of ventilation mode over the year.

    Parameters
    ----------
    df_vent_mode : pandas.DataFrame
        Input table for ventilation mode counts by month.

    display : {'auto', 'inline', 'browser', 'none'}, default 'auto'
        Display mode.
        - 'auto': use 'inline' in notebooks, otherwise 'browser'
        - 'inline': display in notebook output. Altair charts work out-of-the-box on Jupyter Notebook, JupyterLab, Zeppelin, and related notebook environments.
        - 'browser': display chart in an external web browser.
        - 'none': do not display
    save : bool, default False
        If True, save chart to ``fp`` (or a default filename when ``fp`` is None).
    fp : string filename or file-like object, default None
        File in which to write the chart.
        The file format to write is inferred from the extension and must be one of
        ['json', 'html', 'png', 'svg', 'pdf'].

    Returns
    -------
    alt.Chart
        The composed Altair chart object.
    """

    df_vent_mode.drop(df_vent_mode.tail(1).index,inplace=True)
    df_vent_mode = df_vent_mode.stack().reset_index()
    df_vent_mode.columns = ['month', 'mode', 'value']
    df_vent_mode['mode'] = df_vent_mode['mode'].astype(str)

    bars = alt.Chart(df_vent_mode).mark_bar().encode(
        x=alt.X('sum(value):Q').stack("normalize"),
        y=alt.Y('month:N', sort=None ),
        color=alt.Color(
            'mode',
            legend=alt.Legend(
                title='Ventilative Cooling (VC) mode',
                labelExpr="{'0':'VC mode [0]: ventilative cooling not required','1':'VC mode [1]: potential comfort hrs by direct ventilative cooling with minimum airflow rates','2':'VC mode [2]: potential comfort hrs by direct ventilative cooling with increased airflow rates','3':'VC mode [3]: residual discomfort hrs'}[datum.label]",
                labelLimit= 550
            )
        ),
        tooltip=[
            alt.Tooltip('mode:Q', title='VC mode'),
            alt.Tooltip('value:Q')
        ]
    ).interactive()

    text = alt.Chart(df_vent_mode).mark_text(
        dx=-15, dy=3, color='white'
        ).encode(
        x=alt.X('sum(value):Q').stack('normalize'),
        y=alt.Y('month:N', sort=None),
        detail='mode:N',
        text=alt.condition(alt.datum.value > 50,
            alt.Text('value:Q', format='.0f'),
            alt.value('')
        ),
        order=alt.Order('mode:N'),
    )
    chart = bars + text
    chart = chart.properties(
        width=400,
        title='Distribution of ventilation mode over the year',
        padding=50
    )

    # save chart
    if save:
        if fp is None:
            fp = "vent_mode_over_year.png"
        try:
            chart.save(fp)
        except Exception as e:
            raise e


    # display chart
    if display == "auto":
        display = "inline" if _in_notebook() else "browser"

    try:
        if display == "inline":
            with alt.renderers.enable("default"):
                _display(chart)

        elif display == "browser":
            with alt.renderers.enable("browser"):
                chart.show()

    except Exception as e:
        raise e
    
    return chart



def plot_requirend_frequency_air_change_rate(df_freq_air_change, display="auto", save=False, fp=None):
    """
    Create and (optionally) display/save a combined bar + cumulative-percentage Altair chart of Frequency of air change rate required to provide potential comfort.

    Parameters
    ----------
    df_freq_air_change : pandas.DataFrame
        Output of ``get_requirend_frequency_air_change_rate`` with columns 'frequency' and 'cumulative_percentage'.

    display : {'auto', 'inline', 'browser', 'none'}, default 'auto'
        Display mode.
        - 'auto': use 'inline' in notebooks, otherwise 'browser'
        - 'inline': display in notebook output. Altair charts work out-of-the-box on Jupyter Notebook, JupyterLab, Zeppelin, and related notebook environments.
        - 'browser': display chart in an external web browser.
        - 'none': do not display
    save : bool, default False
        If True, save chart to ``fp`` (or a default filename when ``fp`` is None).
    fp : string filename or file-like object, default None
        File in which to write the chart.
        The file format to write is inferred from the extension and must be one of
        ['json', 'html', 'png', 'svg', 'pdf'].

    Returns
    -------
    alt.Chart
        The composed Altair chart object.
    """

    df = df_freq_air_change.copy()
    df['ach'] = df.index

    base = alt.Chart(df).encode(
        x=alt.X('ach', sort=None),
    )

    bar_chart = base.mark_bar().encode(
        y=alt.Y('frequency', sort=None),
        tooltip=[
            alt.Tooltip('frequency:Q', title='Frequency'),
        ]
    ).interactive()

    line_chart = base.mark_line(color='#57A44C', point={"color": "#57A44C"}).encode(
        y=alt.Y('cumulative_percentage', sort=None).title("cumulative percentage"),
        tooltip=[
            alt.Tooltip('cumulative_percentage:Q', title='cumulative percentage', format='.3f'),
        ]
    )

    chart = alt.layer(bar_chart, line_chart).resolve_scale(
        y='independent'
    )
    chart = chart.properties(
        title="Frequency of air change rate required to provide potential comfort",
        width=400,
        padding=50,
    )
   
    # save chart
    if save:
        if fp is None:
            fp = "requirend_frequency_air_change_rate.png"
        try:
            chart.save(fp)
        except Exception as e:
            raise e


    # display chart
    if display == "auto":
        display = "inline" if _in_notebook() else "browser"

    try:
        if display == "inline":
            with alt.renderers.enable("default"):
                _display(chart)

        elif display == "browser":
            with alt.renderers.enable("browser"):
                chart.show()
    except Exception as e:
        raise e
    
    return chart




def plot_annual_data(df_annual_data, display="auto", save=False, fp=None):
    """
    Create and (optionally) display/save a monthly Altair chart of annual energy data.

    Expected input schema (columns):
    - Month
    - Heating
    - Cooling without ventilative cooling
    - Cooling with ventilative cooling

    A final aggregate row with month='Year' is ignored for plotting.
    """
    # Work on a copy to avoid modifying caller's DataFrame.
    df = df_annual_data.copy()

    df['Month'] = df.index.map(lambda x: calendar.month_abbr[x])
    df_long = df.melt(
        id_vars="Month",
        value_vars=["Heating", "Cooling no VCP", "Cooling VCP"],
        var_name="Type",
        value_name="Value"
    )
    
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X("Type:O", title=""),
        y=alt.Y("Value:Q"),
        color='Type:N',
        column=alt.Column("Month:N", sort=[calendar.month_abbr[i] for i in range(1, 13)]),
        tooltip=["Month", "Type", "Value"]
    ).interactive()

    chart = chart.properties(
        title='Sensible energy needs [kWh]',
        padding=50
    )

    # save chart
    if save:
        if fp is None:
            fp = "annual_data.png"
        try:
            chart.save(fp)
        except Exception as e:
            raise e


    # display chart
    if display == "auto":
        display = "inline" if _in_notebook() else "browser"

    try:
        if display == "inline":
            with alt.renderers.enable("default"):
                _display(chart)

        elif display == "browser":
            with alt.renderers.enable("browser"):
                chart.show()
    except Exception as e:
        raise e
    
    return chart
    