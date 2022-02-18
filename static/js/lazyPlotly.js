(function($) {

    // if vplot div is found on page, load!

    if ($("#vplot").length) {
        var config = {responsive: true}

        var id = $("#vplot").data("fileid");

        req = $.ajax({
            url : "/ajax/telemetry/"+id
        });

        req.done(function(data) {
            if(req.status != 200) {
                console.log("Couldn't load telemetry!");
                return;
            }
            var vplot = JSON.parse(data);
            var plot = Plotly.plot('vplot', vplot, {});
            plot.react(config=config);
            console.log("Lazily loaded telemetry.")
        });

    }

})(jQuery);
