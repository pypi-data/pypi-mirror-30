jQuery(function ($) {
	var play = function () {
		var url = $("table#player").attr("data-stream");
		var html = "<audio preload='none' style='display:none'><source type='audio/mpeg' src='" + url + "'/></audio>";
		$("#player td.np").append(html);
		var p = $("#player audio");
		p[0].play();
		return p;
	};

	$("#player").each(function () {
		var block = $(this),
			audio = null,
			btn_play = block.find("button.play"),
			btn_stop = block.find("button.pause");

		btn_play.click(function (e) {
			e.preventDefault();

			audio = play();

			btn_play.hide();
			btn_stop.show();
		});

		btn_stop.click(function (e) {
			e.preventDefault();

			var a = $("#player audio");
			a[0].pause();
			a[0].src = "";
			a.remove();

			btn_stop.hide();
			btn_play.show();
		});
	});
});
