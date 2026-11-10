"""Large-scale batteries in Germany: map, growth chart and key figures.

Data source: Marktstammdatenregister (MaStR) of the Bundesnetzagentur,
licence dl-de/by-2-0. The script queries the public unit overview
(https://www.marktstammdatenregister.de/MaStR/Einheit/Einheiten/ErweiterteOeffentlicheEinheitenuebersicht)
for all storage units with a net rated power of at least 1 MW.

Usage (from the repository root):

    pip install pandas requests
    python _scripts/battery_map.py            # download a fresh snapshot
    python _scripts/battery_map.py --cached   # reuse the last download

Outputs:
    data/battery_map_germany_2026.html   interactive Leaflet map
    data/battery_map_germany_2022.html   the October 2022 data in the same style
    _includes/battery_growth_2026.svg    bar chart of yearly additions
    key figures for the blog post on stdout

The side-by-side image in the post is a screenshot of both maps, see
_scripts/screenshot_maps.js.
"""

import argparse
import json
from datetime import date
from pathlib import Path
from string import Template

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path(__file__).resolve().parent / "mastr_storage_snapshot.json"
MAP_FILE = ROOT / "data" / "battery_map_germany_2026.html"
MAP_FILE_2022 = ROOT / "data" / "battery_map_germany_2022.html"

# Manual CSV exports from the MaStR web interface of 6 October 2022, as used
# for the first version of the map (one file per battery technology).
DATA_2022 = Path(__file__).resolve().parent / "data_2022"
FILES_2022 = {
    "storage_liion.csv": "Lithium-ion",
    "storage_lead.csv": "Lead-acid",
    "storage_heat.csv": "High-temperature",
}
SNAPSHOT_2022 = "2022-10-06"
CHART_FILE = ROOT / "_includes" / "battery_growth_2026.svg"

API_URL = (
    "https://www.marktstammdatenregister.de/MaStR/Einheit/EinheitJson/"
    "GetErweiterteOeffentlicheEinheitStromerzeugung"
)
ENERGY_CARRIER_STORAGE = 2496
MIN_POWER_KW = 1000
PAGE_SIZE = 5000

# Usable capacity is often entered in the wrong unit (Wh, MWh). Units outside
# this energy-to-power range stay on the map, but are left out of energy figures.
PLAUSIBLE_E_TO_P_HOURS = (0.1, 10)

STATUS = {
    "In Betrieb": "operating",
    "In Planung": "planned",
    "Vorübergehend stillgelegt": "mothballed",
}
TECHNOLOGY = {
    727: "Lithium-ion",
    728: "Lead-acid",
    729: "Redox flow",
    730: "High-temperature",
    731: "Nickel-based",
    732: "Other",
}
NATURAL_PERSON = 518

# Same colours as in the 2022 map; "Other" is new (redox flow, nickel-based,
# other and unspecified technologies were below the 1 MW filter back then).
TECHNOLOGY_GROUP = {
    "Lithium-ion": "Li-ion",
    "Lead-acid": "Lead",
    "High-temperature": "High-temperature",
}
COLORS = {
    "Li-ion": "#8541f2",
    "Lead": "#525354",
    "High-temperature": "#a32727",
    "Other": "#199e70",
}

# Circle radius in pixels = RADIUS_FACTOR * MW ** RADIUS_EXPONENT.
# The 2022 map scaled the radius linearly with power (exponent 1), which
# exaggerates large units: the area grows with the square of the power.
# Scaling the area with power (exponent 0.5) is correct on paper, but readers
# tend to underestimate the area of large circles. Flannery's perceptual
# scaling (exponent 0.57) sits in between and compensates for that.
RADIUS_EXPONENT = 0.57
RADIUS_FACTOR = 1.0
RADIUS_MIN = 1.8


def download():
    """Fetches all storage units >= 1 MW from the public MaStR overview."""
    filter_ = (
        f"Energieträger~eq~'{ENERGY_CARRIER_STORAGE}'"
        f"~and~Nettonennleistung der Einheit~gt~'{MIN_POWER_KW - 1}'"
    )
    rows, page = [], 1
    while True:
        response = requests.get(
            API_URL,
            params={"page": page, "pageSize": PAGE_SIZE, "filter": filter_},
            timeout=300,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("Error"):
            raise RuntimeError(f"MaStR returned an error: {payload}")
        rows += payload["Data"]
        if len(rows) >= payload["Total"] or not payload["Data"]:
            break
        page += 1
    snapshot = {"retrieved": date.today().isoformat(), "units": rows}
    CACHE.write_text(json.dumps(snapshot), encoding="utf-8")
    return snapshot


def parse_date(column):
    """MaStR dates look like '/Date(1617861202179)/' (milliseconds since 1970)."""
    millis = column.str.extract(r"(-?\d+)")[0].astype(float)
    return pd.to_datetime(millis, unit="ms")


def prepare(units):
    """
    keeps batteries only (drops pumped hydro)
    drops decommissioned units
    drops units registered by private individuals (mostly home batteries
    with kW/W mix-ups)
    units without public coordinates are kept for the figures, but cannot
    be shown on the map
    """
    raw = pd.DataFrame(units)
    data = raw[raw["StromspeichertechnologieBezeichnung"] == "Batterie"].copy()
    data = data[data["Nettonennleistung"] >= MIN_POWER_KW]
    data = data[data["BetriebsStatusName"].isin(STATUS)]
    data = data[data["AnlagenbetreiberPersonenArt"] != NATURAL_PERSON]

    data["status"] = data["BetriebsStatusName"].map(STATUS)
    data["technology"] = data["Batterietechnologie"].map(TECHNOLOGY).fillna("Not specified")
    data["technology_group"] = data["technology"].map(TECHNOLOGY_GROUP).fillna("Other")
    data["power_mw"] = data["Nettonennleistung"] / 1000
    data["energy_mwh"] = data["NutzbareSpeicherkapazitaet"] / 1000
    data["e_to_p"] = data["energy_mwh"] / data["power_mw"]
    low, high = PLAUSIBLE_E_TO_P_HOURS
    data["energy_plausible"] = data["e_to_p"].between(low, high)
    data["commissioned"] = parse_date(data["InbetriebnahmeDatum"])
    data["planned_for"] = parse_date(data["GeplantesInbetriebsnahmeDatum"])
    return data.sort_values("power_mw", ascending=False)


def prepare_2022():
    """Brings the October 2022 CSV exports into the same shape as prepare()."""
    frames = []
    for filename, technology in FILES_2022.items():
        frame = pd.read_csv(DATA_2022 / filename, sep=";", decimal=",")
        frame["technology"] = technology
        frames.append(frame)
    raw = pd.concat(frames, ignore_index=True)

    data = pd.DataFrame(
        {
            "Id": None,
            "MaStRNummer": raw["MaStR-Nr. der Einheit"],
            "EinheitName": raw["Anzeige-Name der Einheit"],
            "BetriebsStatusName": raw["Betriebs-Status"],
            "Breitengrad": raw["Koordinate: Breitengrad (WGS84)"],
            "Laengengrad": raw["Koordinate: Längengrad (WGS84)"],
            "Bundesland": raw["Bundesland"],
            "Ort": raw["Ort"],
            "AnlagenbetreiberName": raw["Name des Anlagenbetreibers (nur Org.)"],
            "technology": raw["technology"],
            "power_mw": raw["Nettonennleistung der Einheit"] / 1000,
            "energy_mwh": raw["Nutzbare Speicherkapazität in kWh"] / 1000,
            "commissioned": pd.to_datetime(
                raw["Inbetriebnahmedatum der Einheit"], dayfirst=True
            ),
            "planned_for": pd.to_datetime(
                raw["Datum der geplanten Inbetriebnahme"], dayfirst=True
            ),
        }
    )
    data = data[data["power_mw"] >= MIN_POWER_KW / 1000]
    data = data[data["BetriebsStatusName"].isin(STATUS)]
    data = data[~data["AnlagenbetreiberName"].str.contains("natürliche", na=False)]
    data = data.dropna(subset=["Bundesland"])  # units abroad (LU, AT)

    data["status"] = data["BetriebsStatusName"].map(STATUS)
    data["technology_group"] = data["technology"].map(TECHNOLOGY_GROUP).fillna("Other")
    data["e_to_p"] = data["energy_mwh"] / data["power_mw"]
    low, high = PLAUSIBLE_E_TO_P_HOURS
    data["energy_plausible"] = data["e_to_p"].between(low, high)
    return data.sort_values("power_mw", ascending=False)


def key_figures(data, retrieved):
    figures = {"retrieved": retrieved}
    for status, group in data.groupby("status"):
        plausible = group[group["energy_plausible"]]
        figures[status] = {
            "units": len(group),
            "power_mw": round(group["power_mw"].sum()),
            "energy_mwh": round(plausible["energy_mwh"].sum()),
            "e_to_p_weighted": round(
                plausible["energy_mwh"].sum() / plausible["power_mw"].sum(), 2
            ),
            "e_to_p_median": round(plausible["e_to_p"].median(), 2),
            "units_without_plausible_energy": len(group) - len(plausible),
            "units_without_coordinates": int(group["Breitengrad"].isna().sum()),
            "share_lithium": round(
                (group["technology"] == "Lithium-ion").sum()
                / (group["technology"] != "Not specified").sum(), 2
            ),
            "largest": group.head(8)[
                ["EinheitName", "power_mw", "energy_mwh", "AnlagenbetreiberName", "Ort"]
            ].to_dict("records"),
            "by_state_mw": group.groupby("Bundesland")["power_mw"].sum().round()
            .sort_values(ascending=False).head(6).to_dict(),
            "by_technology": group["technology"].value_counts().to_dict(),
            "by_operator_mw": group.groupby("AnlagenbetreiberName")["power_mw"].sum()
            .round().sort_values(ascending=False).head(8).to_dict(),
            "share_100mw_plus": round(
                group.loc[group["power_mw"] >= 100, "power_mw"].sum()
                / group["power_mw"].sum(), 2
            ),
        }
    planned = data[data["status"] == "planned"]
    figures["planned"]["overdue_units"] = int((planned["planned_for"] < retrieved).sum())
    figures["planned"]["overdue_mw"] = round(
        planned.loc[planned["planned_for"] < retrieved, "power_mw"].sum()
    )
    figures["planned"]["by_year_mw"] = (
        planned.groupby(planned["planned_for"].dt.year)["power_mw"].sum().round().to_dict()
    )
    figures["additions"] = yearly_additions(data).to_dict("index")
    return figures


def yearly_additions(data):
    """Power and energy of operating units by year of commissioning."""
    operating = data[data["status"] == "operating"]
    year = operating["commissioned"].dt.year
    additions = pd.DataFrame(
        {
            "units": operating.groupby(year).size(),
            "power_mw": operating.groupby(year)["power_mw"].sum().round(),
            "energy_mwh": operating[operating["energy_plausible"]]
            .groupby(year)["energy_mwh"].sum().round(),
        }
    )
    additions.index = additions.index.astype(int)
    return additions


def format_date(timestamp):
    return "" if pd.isna(timestamp) else timestamp.strftime("%b %Y")


def map_records(data):
    records = []
    located = data.dropna(subset=["Breitengrad", "Laengengrad"])
    for _, unit in located.iterrows():
        records.append(
            {
                "id": None if pd.isna(unit["Id"]) else int(unit["Id"]),
                "mastr": unit["MaStRNummer"],
                "name": unit["EinheitName"] if pd.notna(unit["EinheitName"]) else "",
                "status": unit["status"],
                "lat": round(unit["Breitengrad"], 4),
                "lon": round(unit["Laengengrad"], 4),
                "mw": round(unit["power_mw"], 1),
                "mwh": round(unit["energy_mwh"], 1) if unit["energy_plausible"] else None,
                "date": format_date(
                    unit["planned_for"] if unit["status"] == "planned" else unit["commissioned"]
                ),
                "operator": unit["AnlagenbetreiberName"]
                if pd.notna(unit["AnlagenbetreiberName"]) else "",
                "place": ", ".join(
                    p for p in (unit["Ort"], unit["Bundesland"]) if pd.notna(p)
                ),
                "tech": unit["technology"],
                "group": unit["technology_group"],
            }
        )
    return records


MAP_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Large-scale batteries in Germany ($retrieved_long)</title>
<link rel="stylesheet" href="/data/leaflet/leaflet.css">
<style>
  html, body, #map { height: 100%; margin: 0; }
  body { font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  .legend { background: #fff; padding: 8px 10px; border-radius: 5px; box-shadow: 0 1px 5px rgba(0,0,0,.4); color: #111; }
  .legend h1 { font-size: 14px; margin: 0 0 2px; }
  .legend p { margin: 0 0 6px; color: #52514e; font-size: 12px; }
  .legend label { display: block; cursor: pointer; white-space: nowrap; }
  .legend .dot { display: inline-block; box-sizing: border-box; width: 11px; height: 11px; border-radius: 50%; margin: 0 4px 0 2px; vertical-align: -1px; border: 1.5px solid #52514e; }
  .legend .dot.operating { background: #52514e; }
  .legend .dot.mothballed { border-style: dotted; }
  .legend .techs { margin-top: 6px; }
  .legend .techs div { white-space: nowrap; }
  .legend .techs .dot { border: 0; }
  .sizes { position: relative; font-size: 12px; color: #52514e; }
  .sizes span { position: absolute; left: 0; bottom: 0; box-sizing: border-box; border: 1px solid #52514e; border-radius: 50%; }
  .sizes em { position: absolute; font-style: normal; white-space: nowrap; border-top: 1px solid #b5b4ae; padding-left: 22px; text-align: right; line-height: 0; }
  .sizes em b { font-weight: normal; background: #fff; padding-left: 3px; }
  @media (max-width: 500px) { .legend.size-legend, .legend p, .legend .techs .count { display: none; } .legend { font-size: 12px; padding: 6px 8px; } .legend h1 { font-size: 12px; } }
  .leaflet-popup-content { font-size: 13px; line-height: 1.5; }
  .leaflet-popup-content b.title { font-size: 14px; }
</style>
</head>
<body>
<div id="map"></div>
<script src="/data/leaflet/leaflet.js"></script>
<script>
var UNITS = $units;
var COLORS = $colors;
var TOTALS = $totals;
var TECH_COUNTS = $tech_counts;

// "?static" hides the zoom buttons (used for screenshots)
var isStatic = location.search.indexOf('static') >= 0;
var map = L.map('map', {preferCanvas: true, zoomSnap: 0.5, zoomControl: !isStatic});
map.fitBounds([[47.2, 5.9], [55.3, 15.05]]);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | ' +
    'Data: <a href="https://www.marktstammdatenregister.de/">Marktstammdatenregister</a> ' +
    '(<a href="https://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a>), $retrieved_long'
}).addTo(map);

function esc(text) {
  var div = document.createElement('div');
  div.textContent = text == null ? '' : String(text);
  return div.innerHTML;
}
function radius(mw) { return Math.max($radius_min, $radius_factor * Math.pow(mw, $radius_exponent)); }
function fmt(value) { return value.toLocaleString('en-US', {maximumFractionDigits: 1}); }

function popup(u) {
  var rows = ['<b class="title">' + esc(u.name) + '</b>',
    '<b>Status:</b> ' + u.status + (u.date ? ' (' + (u.status === 'planned' ? 'planned for ' : 'since ') + u.date + ')' : ''),
    '<b>Rated power:</b> ' + fmt(u.mw) + ' MW'];
  if (u.mwh != null) {
    rows.push('<b>Capacity:</b> ' + fmt(u.mwh) + ' MWh (' + fmt(u.mwh / u.mw) + ' h)');
  }
  rows.push('<b>Technology:</b> ' + esc(u.tech));
  if (u.operator) rows.push('<b>Operator:</b> ' + esc(u.operator));
  rows.push('<b>Location:</b> ' + esc(u.place));
  rows.push('<b>MaStR:</b> ' + (u.id == null ? esc(u.mastr) :
    '<a target="_blank" rel="noopener" href="https://www.marktstammdatenregister.de/MaStR/Einheit/Detail/IndexOeffentlich/' +
    u.id + '">' + esc(u.mastr) + '</a>'));
  return rows.join('<br>');
}

// Colour = technology. Status: filled = operating, ring = planned, dotted ring = mothballed.
var STYLE = {
  operating: {weight: 0.5, fillOpacity: 0.6},
  planned: {weight: 1, fillOpacity: 0.08},
  mothballed: {weight: 0.8, fillOpacity: 0.08, dashArray: '2 3'}
};
// planned first, so that operating units are drawn on top
var order = ['planned', 'mothballed', 'operating'];
var layers = {};
order.forEach(function (status) {
  layers[status] = L.layerGroup().addTo(map);
  UNITS.filter(function (u) { return u.status === status; }).forEach(function (u) {
    var style = {radius: radius(u.mw), color: COLORS[u.group], fillColor: COLORS[u.group]};
    for (var key in STYLE[status]) { style[key] = STYLE[status][key]; }
    L.circleMarker([u.lat, u.lon], style).bindPopup(popup(u), {maxWidth: 340}).addTo(layers[status]);
  });
});

var legend = L.control({position: 'topright'});
legend.onAdd = function () {
  var div = L.DomUtil.create('div', 'legend');
  var html = '<h1>Batteries &ge; 1 MW in Germany</h1><p>as of $retrieved_long</p>';
  ['operating', 'planned', 'mothballed'].forEach(function (status) {
    html += '<label><input type="checkbox" checked data-status="' + status + '">' +
      '<span class="dot ' + status + '"></span>' +
      status.charAt(0).toUpperCase() + status.slice(1) + ' &ndash; ' + TOTALS[status] + '</label>';
  });
  html += '<div class="techs">';
  Object.keys(COLORS).forEach(function (group) {
    html += '<div><span class="dot" style="background:' + COLORS[group] + '"></span>' + group +
      '<span class="count"> (' + (TECH_COUNTS[group] || 0) + ')</span></div>';
  });
  html += '</div>';
  div.innerHTML = html;
  L.DomEvent.disableClickPropagation(div);
  div.addEventListener('change', function (event) {
    var layer = layers[event.target.getAttribute('data-status')];
    if (event.target.checked) { layer.addTo(map); } else { map.removeLayer(layer); }
  });
  return div;
};
legend.addTo(map);

// nested circles as size legend
var sizeLegend = L.control({position: 'bottomright'});
sizeLegend.onAdd = function () {
  var div = L.DomUtil.create('div', 'legend size-legend');
  var sizes = [1000, 100, 10];
  var max = 2 * radius(sizes[0]);
  var html = '<div class="sizes" style="width:' + (max + 62) + 'px;height:' + max + 'px">';
  sizes.forEach(function (mw) {
    var d = 2 * radius(mw);
    html += '<span style="width:' + d + 'px;height:' + d + 'px;left:' + (max - d) / 2 + 'px"></span>' +
      '<em style="left:' + max / 2 + 'px;bottom:' + d + 'px;width:' + (max / 2 + 62) + 'px;box-sizing:border-box"><b>' +
      mw.toLocaleString('en-US') + ' MW</b></em>';
  });
  div.innerHTML = html + '</div>';
  return div;
};
sizeLegend.addTo(map);
</script>
</body>
</html>
"""
)


def gw(mw):
    return f"{mw / 1000:.1f} GW" if mw >= 1000 else f"{mw:.0f} MW"


def write_map(data, retrieved, map_file):
    totals = {status: gw(0) for status in STATUS.values()}
    totals.update(
        {status: gw(group["power_mw"].sum()) for status, group in data.groupby("status")}
    )
    html = MAP_TEMPLATE.substitute(
        units=json.dumps(map_records(data), ensure_ascii=False, separators=(",", ":"))
        .replace("</", "<\\/"),
        colors=json.dumps(COLORS),
        totals=json.dumps(totals),
        tech_counts=json.dumps(data["technology_group"].value_counts().to_dict()),
        radius_exponent=RADIUS_EXPONENT,
        radius_factor=RADIUS_FACTOR,
        radius_min=RADIUS_MIN,
        retrieved_long=f"{retrieved.day} {retrieved:%B %Y}",
    )
    map_file.write_text(html, encoding="utf-8")


def write_chart(data, retrieved, first_year=2016):
    """Column chart of yearly capacity additions as a plain SVG (no dependencies)."""
    additions = yearly_additions(data)["power_mw"]
    years = list(range(first_year, retrieved.year + 1))
    values = [float(additions.get(year, 0)) for year in years]

    width, height = 740, 340
    left, right, top, bottom = 52, 12, 28, 34
    plot_w, plot_h = width - left - right, height - top - bottom
    step = 500
    y_max = step * (int(max(values) / step) + 1)
    slot = plot_w / len(years)
    bar_w = min(24, slot * 0.6)

    def y(value):
        return top + plot_h * (1 - value / y_max)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-labelledby="battery-growth-title" style="max-width:100%;height:auto;'
        f'font-family:inherit;font-size:13px">',
        f'<title id="battery-growth-title">Rated power of batteries of at least 1 MW '
        f"commissioned in Germany per year, {years[0]} to {years[-1]}</title>",
        f'<text x="0" y="14" fill="#52514e">MW commissioned per year</text>',
    ]
    for tick in range(0, y_max + 1, step):
        parts.append(
            f'<line x1="{left}" x2="{width - right}" y1="{y(tick):.1f}" y2="{y(tick):.1f}" '
            f'stroke="{"#52514e" if tick == 0 else "#e4e3de"}" stroke-width="1"/>'
            f'<text x="{left - 8}" y="{y(tick) + 4:.1f}" text-anchor="end" fill="#52514e">'
            f"{tick:,}</text>"
        )
    for i, (year, value) in enumerate(zip(years, values)):
        x = left + slot * i + (slot - bar_w) / 2
        h = plot_h * value / y_max
        r = min(4, h)
        # column with rounded top and square baseline
        path = (
            f"M{x:.1f},{y(0):.1f} v{-(h - r):.1f} q0,{-r} {r},{-r} h{bar_w - 2 * r:.1f} "
            f"q{r},0 {r},{r} v{h - r:.1f} z"
        )
        partial = year == retrieved.year
        label = f"{year}{'*' if partial else ''}"
        parts.append(
            f'<path d="{path}" fill="{COLORS["Li-ion"]}"><title>{label}: {value:,.0f} MW'
            f"</title></path>"
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 12}" text-anchor="middle" '
            f'fill="#52514e">{label}</text>'
        )
        if value == max(values) or year == years[-2]:
            parts.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y(value) - 6:.1f}" text-anchor="middle" '
                f'fill="#0b0b0b">{value:,.0f}</text>'
            )
    parts.append("</svg>")
    CHART_FILE.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cached", action="store_true", help="reuse the last download")
    args = parser.parse_args()

    snapshot = json.loads(CACHE.read_text(encoding="utf-8")) if args.cached else download()
    retrieved = pd.Timestamp(snapshot["retrieved"])
    data = prepare(snapshot["units"])

    write_map(data, retrieved, MAP_FILE)
    write_map(prepare_2022(), pd.Timestamp(SNAPSHOT_2022), MAP_FILE_2022)
    write_chart(data, retrieved)
    print(json.dumps(key_figures(data, retrieved.date().isoformat()), indent=2,
                     ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
