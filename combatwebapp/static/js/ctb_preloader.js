/**
 * Created by thoba on 2016/03/31.
 */

//GoogleAnalytics
(function (i, s, o, g, r, a, m) {
    i['GoogleAnalyticsObject'] = r;
    i[r] = i[r] || function () {
            (i[r].q = i[r].q || []).push(arguments)
        }, i[r].l = 1 * new Date();
    a = s.createElement(o),
        m = s.getElementsByTagName(o)[0];
    a.async = 1;
    a.src = g;
    m.parentNode.insertBefore(a, m)
})(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

ga('create', 'UA-67570323-5', 'auto');
ga('send', 'pageview');


$(function () {

    $('#preloader').hide();

    $('#search').keypress(function (e) {
        if (e.keyCode === 13) { //When Enter is pressed
            $('#preloader').show();
        }
    });
});


