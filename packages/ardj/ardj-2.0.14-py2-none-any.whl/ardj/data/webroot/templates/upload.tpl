{% extends "base.tpl" %}

{% block content %}
  <div class="page-header">
    <h1>Upload music</h1>
  </div>

  <form method="post" class="form wait async_files">
    <div class="form-group">
      <label>Labels:</labels>
      <input type="text" class="form-control" name="labels" value="tagme, music"/>
    </div>

    <div class="form-group">
      <label class="btn btn-primary">Select files<input type="file" name="file" multiple="multiple" class="autosubmit"/></label>
    </div>
  </form>
{% endblock %}
