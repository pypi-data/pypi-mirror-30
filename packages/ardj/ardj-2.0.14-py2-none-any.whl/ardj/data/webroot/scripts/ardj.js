/**
 * Simplifies substring replacement.  Usage:
 * alert("{a}, {b}!".format({a: "hello", b: "world"}));
 */
function fmt(s, args)
{
    var formatted = s;
    for (arg in args) {
        var repeat = true;
        while (repeat) {
            var tmp = formatted.replace("{" + arg + "}", args[arg]);
            if (tmp == formatted)
                repeat = false;
            else
                formatted = tmp;
        }
    }
    return formatted;
};

jQuery(function ($) {
    $(document).on("click", "button.trigger", function (e) {
        e.preventDefault();
        $(this).blur();
        $(document).trigger($(this).attr("data-trigger"));
    });

    $(document).on("click", ".hometabs a", function (e) {
        e.preventDefault();
        $(this).blur();

        var tab_id = $(this).attr("href").substr(1);
        $(".tab").hide();
        $("#" + tab_id + "_tab").show();

        $(this).closest("ul").find("li").removeClass("active");
        $(this).closest("li").addClass("active");
    });

    $(document).on("ardj.home.refresh", function (e) {
        $.ajax({
            url: "/",
            type: "GET",
            dataType: "html"
        }).done(function (res) {
            $("#queue_tab").html($(res).find("#queue_tab").html());
            $("#recent_tab").html($(res).find("#recent_tab").html());
        });
    });
});


/**
 * Replacement alert.
 *
 * Replace the built in alert function with an html message box, if there is one.
 **/
jQuery(function ($) {
    $("#msgbox:first").each(function (e) {
        var box = $(this);
        box.hide();

        var timer = null;

        window.alert = function (msg) {
            if (timer !== null) {
                clearTimeout(timer);
                timer = null;
            }

            box.html(msg);
            box.show();

            timer = setTimeout(function () {
                box.hide("slow");
            }, 5000);
        };

    });
});

// vim: set ts=4 sts=4 sw=4 et:
