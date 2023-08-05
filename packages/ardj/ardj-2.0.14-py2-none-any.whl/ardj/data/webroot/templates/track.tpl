{% extends "base.tpl" %}

{% block content %}
  <div class="page-header">
    <h1>Track properties</h1>
  </div>

  <form method="post" class="form async wait">
    <div class="form-group">
      <label>Title:</label>
      <input type="text" class="form-control" name="title" value="{{ track.title }}" />
    </div>

    <div class="form-group">
      <label>Artist:</label>
      <input type="text" class="form-control" name="artist" value="{{ track.artist }}" />
    </div>

    <div class="form-group">
      <label>Labels:</label>
      <input type="text" class="form-control" name="labels" value="{{ track.labels }}" />
    </div>

    <div class="form-group">
      <label>File name:</label>
      <input type="text" class="form-control" value="{{ track.filename }}" readonly="readonly" />
      <p class="help-block">This is not editable, FYI only, in case there are no tags.</p>
    </div>

    <div class="checkbox">
      <label><input type="checkbox" name="delete" value="yes"/> Delete this track</label>
    </div>

    <div class="checkbox">
      <label><input type="checkbox" name="tagme" value="yes" checked="yes"/> Go to next untagged track after saving</label>
    </div>

    <div class="form-group">
      <button class="btn btn-primary">Save changes</button>
    </div>
  </form>
{% endblock %}
