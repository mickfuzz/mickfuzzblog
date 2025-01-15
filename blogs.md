---
# all the regular stuff you have here
title: Blog Posts
zotero:
  scannable-cite: false # only relevant when your compiling to scannable-cite .odt
  client: zotero # defaults to zotero
  author-in-text: false # when true, enabled fake author-name-only cites by replacing it with the text of the last names of the authors
  csl-style: harvard # pre-fill the style

...

<ul>
  {% for post in site.categories.blogs reversed %}
    {% if post.url %}
        <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a></li>
    {% endif %}
  {% endfor %}
</ul>
