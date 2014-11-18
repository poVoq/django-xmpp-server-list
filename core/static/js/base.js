var register_popover = function() {
    $('.popover-field').popover({
        html: true,
        content: function() {
            var content = '';
            var url = $(this).attr('data-url');
            $.ajax({
                url: url,
                type: 'GET',
                async: false,
            }).done(function(result) {
                content = result;
            });
            return content;
        },
        container: 'body',
        placement: 'bottom',
    });
}
var register_tooltips = function(){
    $('.tooltip-field').tooltip({
        title: function() {
            var tip = $(this).attr('data-tip');
            console.log('#tooltip-' + tip);
            return $('body').find('#tooltip-' + tip).html();
        },
        placement: 'bottom',
        container: 'body',
        html: true,
    });
}

$(document).ready(function() {
    console.log('ready');
    register_tooltips();
    register_popover();

    $('.fblike').on('click', function(event) {
        fblike_button();
    });
});

// Generate a two-click like button.
// Shamelessly stolen from here: http://turkeyland.net/projects/two-click/
var fblike_button = function() {
    // Generate a string containing the HTML to place in the element (for readability)
    var html = "<div id=\"fb-root\">\n";
    html += "<div class=\"fb-like\" data-href=\"https://facebook.com/jabber.at\" data-send=\"true\" data-layout=\"button_count\" data-width=\"100\" data-show-faces=\"false\" data-font=\"arial\">\n";
    html += "</div>\n";

    // Replace the specified element's contents with the HTML necessary to display the
    // Like/+1 Buttons, *before* loading the SDKs below
    $('.fblike').html(html);

    // This is the code provided by facebook to asynchronously load their SDK
    var e = document.createElement('script'); e.async = true;
    e.src = document.location.protocol +
      '//connect.facebook.net/en_US/all.js#xfbml=1';
    document.getElementById('fb-root').appendChild(e);
}
