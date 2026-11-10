---
layout: post
title: "Where are the batteries? The 2026 update"
tags: python energy
image:
  path: /data/preview/battery-map-germany-2026.jpg
  height: 800
  width: 1200
---

Four years ago, I [mapped all large batteries in Germany](/2022/10/07/battery-map-germany.html) and was surprised to find almost 1 GW of them, installed or planned. Time for an update - a lot has happened since.

<iframe src="/data/battery_map_germany_2026.html" title="Interactive map of battery storage projects of at least 1 MW in Germany, November 2026" height="650" width="100%" loading="lazy"></iframe>

[View in full-screen](/data/battery_map_germany_2026.html){:target="_blank"}

The map again shows all battery projects with a rated power of at least 1 MW according to the [Marktstammdatenregister](https://www.marktstammdatenregister.de/){:target="_blank" rel="noopener"}, as of 10 November 2026. Blue circles are in operation, orange ones are registered as planned. The circle area scales with the rated power, and you can switch each group on and off in the legend. Click on a circle for details.

## From megawatts to gigawatts

| | Autumn 2022 | November 2026 |
|---|---|---|
| In operation | approx. 0.65 GW | **4.5 GW** / 8.0 GWh (550 units) |
| Registered as planned | approx. 0.4 GW | **12.8 GW** / 37 GWh (696 units) |
| Largest unit in operation | 66 MW | 140 MW |
| Largest planned unit | 73 MW | 1,000 MW |

The operating fleet has grown roughly sevenfold. And it is accelerating: 1.9 GW went online in 2026 so far, compared to 2.6 GW in all the years before combined.

<figure>
{% include battery_growth_2026.svg %}
<figcaption><small>Rated power of batteries (at least 1 MW) by year of commissioning. *2026 until 10 November. Hover over a bar for the value.</small></figcaption>
</figure>

A few things I find interesting:

* **Batteries are getting longer.** In 2022, the average energy-to-power (E/P) ratio was around 1.3 h. The operating fleet is now at 1.8 h, the typical new project has 2 h, and the planned projects average 2.9 h - driven by some very large 4 h systems.
* **The pipeline is dominated by giants.** Almost two thirds of the planned capacity comes from projects of 100 MW and more. LEAG alone has registered 4.6 GW at its lignite sites in Lusatia and near Leipzig, including four units of 1 GW / 4 GWh each. RWE follows with 1.2 GW at power plant sites such as Hamm and Gundremmingen. Reusing existing grid connection points seems to be the name of the game.
* **The geography is shifting.** Bavaria leads the operating fleet (0.9 GW, spread over almost 200 mostly small units), followed by North Rhine-Westphalia and Saxony-Anhalt. If the plans materialise, Saxony (2.9 GW) and Brandenburg (2.6 GW) will take over.
* **It is still a lithium-ion story.** About 95 % of the operating units use lithium-ion batteries.

## Some words of caution

"Planned" means registered as planned, not financed or under construction. About 250 of the planned units (1.4 GW) have a planned commissioning date that has already passed - some of them are probably online and not yet updated, others may never be built. On the other hand, many projects with a grid connection request do not show up in the register at all.

The data is entered by the operators and is not free of errors. As in 2022, I dropped decommissioned units and units registered by private individuals (mostly home batteries with a kW/W mix-up). For the energy figures, I ignored a handful of units with an implausible E/P ratio (below 0.1 h or above 10 h). Five operating units (158 MW, among them the Big Battery Lausitz) have no public coordinates: they are included in the figures, but missing on the map.

## How it is made

The data has an open [license](https://www.govdata.de/dl-de/by-2-0){:target="_blank" rel="noopener"} and can be queried directly from the register's public unit overview, so the map can be reproduced with a single [Python script](https://github.com/0-k/0-k.github.io/blob/master/_scripts/battery_map.py){:target="_blank" rel="noopener"}. It uses pandas for the data preparation and writes a plain [Leaflet](https://leafletjs.com/){:target="_blank" rel="noopener"} map. The [2022 version](https://github.com/0-k/energy_maps){:target="_blank" rel="noopener"} is still online for comparison.
