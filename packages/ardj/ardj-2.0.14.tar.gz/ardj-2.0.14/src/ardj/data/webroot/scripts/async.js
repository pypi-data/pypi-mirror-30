/**
 * Asynchronous forms with upload progress.
 **/
jQuery(function ($) {
    var handle_json = function (res) {
        res = $.extend({
            message: null,
            confirm: null,
            next: null,
            redirect: null,
            tab_open: null,
            refresh: false,
            trigger: null
        }, res);

		var blur = true;

        if (res.message)
            alert(res.message);

        if (res.trigger)
            $(document).trigger(res.trigger);

        if (res.confirm && res.next) {
            if (!confirm(res.confirm)) {
                $("body").removeClass("wait");
                return;
            }

            $.ajax({
                url: res.next,
                type: "GET",
                dataType: "json"
            }).done(function (res) {
                handle_json(res);
            }).fail(handle_ajax_failure);

            return;
        }

        else if (res.refresh) {
            window.location.reload();
			blur = false;
        } else if (res.redirect) {
            window.location.href = res.redirect;
			blur = false;
        } else if (res.tab_open) {
            window.open(res.tab_open, "_blank");
        }

        if (blur)
            $("body").removeClass("wait");
    };

    var handle_ajax_failure = function (xhr, status, message) {
        if (xhr.status == 404)
            alert("Form handler not found.");
        else if (message == "Debug Output")
            alert(xhr.responseText);
        else if (status == "error" && message == "")
            ;  // aborted, e.g. F5 pressed
        else if (xhr.responseText)
            alert("Request failed." + xhr.responseText);
        else
            alert("Request failed: " + message + "\n\n" + xhr.responseText);

        $("body").removeClass("wait");
    };

    $(document).on("submit", "form.async_files", function (e) {
		var wait = $(this).hasClass("wait");
		if (wait)
			$("body").addClass("wait");

        if (window.FormData === undefined) {
            // alert("File uploads not supported by your browser.");
        } else {
            var pgs = $(this).find(".progress");

            var fd = new FormData($(this)[0]);
            fd.append("_random", Math.random());

            var show_progress = function (percent) {
                pgs.find(".done").css("width", parseInt(percent) + "%");
                pgs.show();
            };

            $.ajax({
                url: $(this).attr("action"),
                type: "POST",
                data: fd,
                processData: false,
                contentType: false,
                cache: false,
                dataType: "json",
                xhr: function () {
                    var xhr = $.ajaxSettings.xhr();
                    xhr.upload.onprogress = function (e) {
                        var pc = Math.round(e.loaded / e.total * 100);
                        show_progress(pc);
                    };
                    return xhr;
                }
            }).done(function (res) {
                handle_json(res);
            }).fail(handle_ajax_failure);

            e.preventDefault();
        }
    });

    $(document).on("change", "form input.autosubmit", function (e) {
        $(this).closest("form").submit();
    });

    $(document).on("click", "a.async", function (e) {
        e.preventDefault();
        $(this).blur();

		var wait = $(this).closest(".wait").length > 0;
		if (wait)
			$("body").addClass("wait");

        $.ajax({
            url: $(this).attr("href"),
            dataType: "json",
            type: $(this).is(".post") ? "POST" : "GET"
        }).done(function (res) {
            handle_json(res);
        }).fail(handle_ajax_failure);
    });

    $(document).on("submit", "form.async", function (e) {
        e.preventDefault();

		var wait = $(this).hasClass("wait");
		if (wait)
			$("body").addClass("wait");

        $.ajax({
            url: $(this).attr("action"),
            data: $(this).serialize(),
            dataType: "json",
            type: $(this).attr("method")
        }).done(function (res) {
            handle_json(res);
        }).fail(handle_ajax_failure);
    });
});
