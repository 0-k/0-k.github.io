---
layout: post
title: "Shopify's API via GraphQL in Python"
tags: python graphql shopify
---

GraphQL is a query language for APIs. It allows to define the structure of the requested data, which makes it possible to avoid returning overly large amounts of data.

[Shopify's Admin API can be queried with GraphQL](https://shopify.dev/api/admin-graphql#top). GraphQL queries are executed by sending POST HTTP requests. This can be achieved in Python with the `requests` module like so:

{% highlight ruby %}
import requests
import json

url = 'https://your-shops-name.myshopify.com/admin/api/2022-01/graphql.json'
headers = {"Content-Type": "application/graphql",
           "X-Shopify-Access-Token": YOUR_ACCESS_TOKEN}

request = requests.post(url, data=your_query, headers=headers)
print(json.loads(request.text))
{% endhighlight %}

Set your API access keyword in `YOUR_ACCESS_TOKEN`. There are many examples given on how to structure the queries. Here is a simple example to get your 10 latest orders:

{% highlight ruby %}
your_query = """
{
  orders(first: 10) {
    edges {
      node {
        id
      }
    }
  }
}
"""
{% endhighlight %}

Happy querying!
