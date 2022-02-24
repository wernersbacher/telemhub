(function($) {

    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })

    // if vplot div is found on page, load!
    if ($("#vplot").length) {
        var config = {responsive: true}

        var id = $("#vplot").data("fileid");
        var cid = Cookies.get('compareID'); // get cookie id
        data = {};

        if (cid)
            data["cid"] = cid
        console.log(data)

        req = $.ajax({
            url : "/ajax/telemetry/"+id,
            type: 'POST',
            data: data
        });

        req.done(function(data) {
            if(req.status != 200) {
                console.log("Couldn't load telemetry!");
                return;
            }
            var vplot = JSON.parse(data);
            var plot = Plotly.plot('vplot', vplot, {});
            console.log("Lazily loaded telemetry.")
        });

    }

})(jQuery);
