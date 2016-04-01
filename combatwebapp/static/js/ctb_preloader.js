/**
 * Created by thoba on 2016/03/31.
 */
$(function () {

    $('#preloader').hide();

    $('#search').keypress(function (e) {
        if (e.keyCode === 13) { //When Enter is pressed
            $('#preloader').show();
        }
    });
});