<!DOCTYPE html>
<!-- vim: set ts=2 sts=2 sw=2 et: -->
<html lang="en">
<head>
  <meta charset="utf-8"/>

  <title>{% block page_title %}{% if page_title %}{{ page_title }}{% else %}{{ site_name }}{% endif %}{% endblock %}</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Language" content="en" />

  <!--
  <meta name="description" content="" />
  <meta name="keywords" content="" />
  <meta name="robots" content="all" />
  -->

  <meta name="viewport" content="width=device-width, initial-scale=1"/>

  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">

  <link rel="stylesheet" type="text/css" href="/styles/bootstrap.min.css"/>
  <link rel="stylesheet" type="text/css" href="/styles/bootstrap-theme.css"/>
  <link rel="stylesheet" type="text/css" href="/styles/screen.css"/>

  <script type="text/javascript" src="/scripts/jquery-1.11.2.min.js"></script>
  <script type="text/javascript" src="/scripts/bootstrap.min.js"></script>
  <script type="text/javascript" src="/scripts/async.js"></script>
  <script type="text/javascript" src="/scripts/player.js"></script>
  <script type="text/javascript" src="/scripts/np.js"></script>
  <script type="text/javascript" src="/scripts/ardj.js"></script>
</head>

<body class="bootstrap{% if body_class %} {{ body_class }}{% endif %}">

  <nav class="navbar navbar-default">
    <div class="container">
      <div class="navbar-header">
        <a href="/" class="navbar-brand" title="Home page">{{ site_name }}</a>
      </div>

      <div class="collapse navbar-collapse">
        <ul class="nav navbar-nav">
          <li{% if tab == "recent" %} class="active"{% endif %}><a href="/">Dashboard</a></li>
          <li{% if tab == "playlist" %} class="active"{% endif %}><a href="/playlist">Playlist</a></li>
          <li><a href="/docs/index.html">Docs</a></li>
          <li><a href="/upload">Upload music</a></li>
        </ul>
      </div>
    </div>
  </nav>

  {% block container %}
    <div class="container">
      {% block content %}{% endblock %}
    </div>
  {% endblock %}

  {% block footer %}
    <footer class="footer">
      <div class="container">
        <!-- hello dear -->
      </div>
    </footer>
  {% endblock %}

  <div id="wait_block"></div>
  <div id="msgbox" class="alert alert-info" style="display:none"></div>
</body>
</html>
