{% extends "base.tpl" %}

{% block content %}
  <div class="page-header">
    <h1>Edit playlist</h1>
  </div>

  <form method="post" class="form wait async playlist"/>
    <div class="form-group">
      <textarea class="form-control" name="contents">{{ contents }}</textarea>
      <p class="help-block">Read <a href="/docs/playlists.html">the fine manual</a> to understand how this work (it's really simple).  This is a <a href="https://en.wikipedia.org/wiki/YAML">YAML file</a>, so mind the leading spaces.</p>
    </div>

    <div class="form-group">
      {% if editable %}
        <button class="btn btn-primary">Save</button>
      {% else %}
        <p>Oops, looks like the file is write-protected.  You cannot make changes online.</p>
      {% endif %}
    </div>
  </form>
{% endblock %}
