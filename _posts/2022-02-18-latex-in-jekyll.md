---
layout: post
title: "LaTeX in Jekyll"
mathjax: true
tags: javascript jekyll latex
---


[MathJax](http://docs.mathjax.org/en/v2.7-latest/start.html#using-a-content-delivery-network-cdn) allows you to include mathematics in your web pages, e.g. by using LaTeX. The formulae will be processed using JavaScript to produce HTML, SVG, or MathML equations for viewing in any modern browser.

It's very easy to include it into your Jekyll posts. Add the following script to `_layouts/post.html`:

{% highlight html %}
<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
{% endhighlight %}

Voilà, you should be good to go. If you now type in your post:

{% highlight latex %}
$$
e^{i\pi} + 1 = 0
$$
{% endhighlight %}

it will render nicely as [Euler's identity](https://en.wikipedia.org/wiki/Euler%27s_identity) as we all know it:
$$
e^{i\pi} + 1 = 0
$$.

Cool! Note that `$$` is required at the beginning and end. It will signify the start and end of the formula formatting.
