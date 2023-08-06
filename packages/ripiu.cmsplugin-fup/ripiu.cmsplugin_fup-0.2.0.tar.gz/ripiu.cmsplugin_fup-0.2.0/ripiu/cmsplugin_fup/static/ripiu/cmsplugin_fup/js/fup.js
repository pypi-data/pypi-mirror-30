$(function() {
    $("mark.ripiu-fup > label").on("click", function(evt) {
        var radio = $("#" + $(this).attr("for"));
        radio.prop("checked", true);
        radio.trigger("change");
        return false;
    });

    $(document).on("touchstart click", function(evt) {
        $(".fup > input").prop("checked", false);
    });

    $("mark.ripiu-fup > label").on("mouseover", function(e) {
        var radio = $("#" + $(this).attr("for"))
        radio.prop("checked", true);
        radio.trigger("change");
    });

    $("mark.ripiu-fup > label").on("mouseout", function(e) {
        var radio = $("#" + $(this).attr("for"))
        radio.prop("checked", false);
        radio.trigger("change");
    });
});
