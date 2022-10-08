---
layout: post
title: Where are the batteries?
tags: python
image:
  path: /data/preview/battery-map-germany.jpg
  height: 100
  width: 100
---

We are entering the age of megawatt-scale batteries. I wondered how far we have come in Germany, so I created this map showing the latest projects.

<iframe src="/data/battery_map_germany.html" height="600" width="100%"></iframe>

[View in full-screen](/data/battery_map_germany.html){:target="_blank"}


The map shows all battery projects (installed or concretely planned) with a rated power of at least 1 MW, according to the [Marktstammdatenregister](https://www.marktstammdatenregister.de/){:target="_blank"}. 
I was surprised to find already almost 1 GW of large-scale battery capacity distributed all over the country. Most of them are li-ion batteries. The projects' average energy-to-power (E/P) ratio is around 1.3 h. I find it interesting to scroll through the list of operators - lots of big names but also projects that seem connected to a local municipality or solar park operator.
As far as I know, the batteries are still mainly operating in the balancing markets, but some projects are adjacent to significant wind and solar projects, so that you could use them for feed-in management.

The data (which has an open [license](https://www.govdata.de/dl-de/by-2-0), by the way) was pretty easy to filter and retrieve. You can check out the source code [here](https://github.com/0-k/energy_maps){:target="_blank"}, where I described the data operations in more detail. 
The project uses the [folium](http://python-visualization.github.io/folium/){:target="_blank"} package, a nice Python wrapper around leaflet.js. 


