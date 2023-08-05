jQuery(function ($) {
	$(".nowplaying").each(function () {
		var msg = $(this);
		var last = null;

		var info = null;
		var delta = 0;

		var format_dur = function (length) {
			var min = parseInt(length / 60);
			var sec = parseInt(length - min * 60);
			var minStr = min + '';
			var secStr = sec + '';
			while (minStr.length < 2) minStr = "0" + minStr;
			while (secStr.length < 2) secStr = "0" + secStr;
			return minStr + ":" + secStr;
		};

		var update = function () {
			var url = "/status.json";
			if (last)
				url += "?last=" + last;

			$.ajax({
				url: url,
				type: "GET",
				dataType: "json"
			}).done(function (res) {
				info = res = $.extend({
					id: null,
					artist: null,
					title: null,
					length: null,
					current_ts: null,
					last_played: null
				}, res);

				// Difference between local and server time.
				if (info.current_ts)
					delta = Date.now() / 1000 - info.current_ts;

				if (last && last != res.id)
					$(document).trigger("ardj.home.refresh");

				last = res.id;

				var message = fmt("{artist} — <a href='/track/{id}' target='_blank'>{title}</a>", {
					artist: res.artist,
					title: res.title,
					id: res.id
				});

				$(".nowplaying").html(message);
			}).always(function () {
				setTimeout(update, 5000);
			});
		};

		// Refresh 1 second after loading the page, then continue as it goes.
		setTimeout(update, 1000);

		// Refresh the progress indicator every second.
		setInterval(function () {
			if (info) {
				var server_time = Date.now() / 1000 - delta;
				var song_pos = server_time - info.last_played;

				// force limits, just in case.
				song_pos = Math.min(Math.max(0, song_pos), info.length);

				var left = Math.round(info.length - song_pos);
				$("#player .left").html("[" + format_dur(left) + "]");

				// percentage
				var pc = Math.round(song_pos * 100 / info.length);
				$(".np .progress .done").css("width", pc + "%");
			}
		}, 500);
	});
});
