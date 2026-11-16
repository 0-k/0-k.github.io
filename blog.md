---
layout: page
title: BLOG
permalink: /blog/
---

<h1>Latest Posts</h1>

<ul>
  {% for post in site.posts %}
    <li>
      <h2><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h2>
      {{ post.excerpt }}
    </li>
  {% endfor %}
</ul>