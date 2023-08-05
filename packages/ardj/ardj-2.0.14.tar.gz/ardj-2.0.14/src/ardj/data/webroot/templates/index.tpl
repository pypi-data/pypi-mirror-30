{% extends "base.tpl" %}

{% block content %}
  <div class="page-header">
    <h1>ardj dashboard</h1>
  </div>

  <table id="player" data-stream="http://127.0.0.1:8000/live.mp3">
    <tbody>
      <tr>
        <td class="buttons rpad">
          <button class="btn btn-small btn-primary play" title="Play"><i class="glyphicon glyphicon-play"></i></button>
          <button class="btn btn-small btn-primary pause" title="Stop" style="display:none"><i class="glyphicon glyphicon-pause"></i></button>
        </td>
        <td class="np"><div class="progress"><div class="done"></div></div><span class="nowplaying">loading...</span><span class="left"></span></td>
        <td class="buttons lpad">
          <a class="btn btn-default btn-small rocks async post" title="ROCKS!" href="/api/rocks"><i class="glyphicon glyphicon-thumbs-up"></i></a>
          <a class="btn btn-default btn-small sucks async post" title="Sucks." href="/api/sucks"><i class="glyphicon glyphicon-thumbs-down"></i></a>
          <a class="btn btn-default btn-small skip async post" title="Skip it." href="/api/skip"><i class="glyphicon glyphicon-forward"></i></a>
        </td>
      </tr>
    </tbody>
  </table>

  <ul class="nav nav-tabs hometabs">
    <li class="active"><a href="#recent">Recent</a></li>
    <li><a href="#queue">Queue</a></li>
  </ul>

  <div id="recent_tab" class="tab">
    {% if tracks %}
      <table class="table tracklist">
        <thead>
          <tr>
            <th/>
            <th class="wide">Track title</th>
            <th class="dur">Dur</th>
          </tr>
        </thead>
        <tbody>
          {% for track in tracks %}
            <tr>
              <td>
                {% if track.image %}
                  <!-- too many errors
                  <img src="{{ track.image }}" alt="cover art"/>
                  -->
                {% endif %}
              </td>
              <td>
                {% if track.artist and track.title %}
                  <a href="/artists/{{ track.artist }}">{{ track.artist }}</a> &mdash; <a href="/track/{{ track.id }}">{{ track.title }}</a>
                {% else %}
                  <a href="/tracks/{{ track.id }}">{{ track.filename }}</a>
                {% endif %}
                <div class="meta">
                  <span class="id" title="track id">#{{ track.id }}</span>
                  <span class="count" title="playback counter">♺{{ track.count }}</span>
                  <span class="weight" title="weight">⚖{{ track.weight }}</span>
                  <a class="btn btn-default btn-xs async" href="/track/{{ track.id }}/queue" title="Add to playback queue"><i class="glyphicon glyphicon-time"></i> queue</a>
                  <a class="btn btn-default btn-xs" href="/track/{{ track.id }}/download" title="Download track"><i class="glyphicon glyphicon-download"></i> download</a>
                </div>
              </td>
              <td class="dur">{{ track.duration }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>Hmm, nothing was played.</p>
      <p>Looks like your radio is not fully set up.  Please <a href="/upload">upload some music</a>.</p>
    {% endif %}
  </div>

  <div id="queue_tab" class="tab" style="display:none">
    {% if queue %}
      <table class="table tracklist">
        <thead>
          <tr>
            <th class="num">#</th>
            <th class="wide">Track title</th>
            <th title="Play count" class="num">Cnt</th>
            <th title="Track weight" class="num">Wgt</th>
            <th class="dur">Dur</th>
          </tr>
        </thead>
        <tbody>
          {% for track in queue %}
            <tr>
              <td class="num">{{ track.id }}</td>
              <td>
                {% if track.artist and track.title %}
                  <a href="/artists/{{ track.artist }}">{{ track.artist }}</a> &mdash; <a href="/track/{{ track.id }}">{{ track.title }}</a>
                {% else %}
                  <a href="/tracks/{{ track.id }}">{{ track.filename }}</a>
                {% endif %}
                <div class="actions">
                  <a class="btn btn-default btn-xs async" href="/track/{{ track.id }}/queue" title="Add to playback queue"><i class="glyphicon glyphicon-time"></i></a>
                  <a class="btn btn-default btn-xs" href="/track/{{ track.id }}/download" title="Download track"><i class="glyphicon glyphicon-download"></i></a>
                  {% for l in track.hlabels %}
                    <a class="btn btn-default btn-xs" href="/tags/{{ l }}" title="Show more track with this label"><i class="glyphicon glyphicon-tag"></i> {{ l }}</a>
                  {% endfor %}
                </div>
              </td>
              <td class="num">{% if track.count %}{{ track.count }}{% else %}—{% endif %}</td>
              <td class="num">{% if track.weight %}{{ track.weight }}{% else %}—{% endif %}</td>
              <td class="dur">{{ track.duration }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>Empty.  Click the buttons to queue some tracks.</p>
    {% endif %}
  </div>

{% endblock %}
