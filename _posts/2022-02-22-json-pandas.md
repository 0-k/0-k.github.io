---
layout: post
title: "JSON and pandas DataFrame"
tags: python
---

JSON (JavaScript Object Notion) is a handy and human-readable file format to exchange data over the internet. pandas DataFrames are _the_ way to handle tabular data in Python. So the natural question is how to convert between the two formats.

Converting a pandas DataFrame to a JSON object is straight-forward:

{% highlight ruby %}
pd.DataFrame.to_json(orient='index')
{% endhighlight %}

The `orient` parameter controls how the [data is formatted](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html). `index` worked well for my use cases so far. 

The other conversion direction is very similar:

{% highlight ruby %}
pd.read_json(your_json_file, orient='index')
{% endhighlight %}

If you receive your JSON as a string in Python (e.g. through a request from an API), you must first convert the string into a JSON object for the above call to work:

{% highlight ruby %}
import json
your_json_file = json.loads(json_as_str)
{% endhighlight %}



