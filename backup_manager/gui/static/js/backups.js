const RESULT_TIME = 2000;

function show_success(button){
    button.addClass('success');
    setTimeout(function () {
        button.removeClass('success');
        }, RESULT_TIME);
}

function show_error(button){
    button.addClass('error');
    setTimeout(function () {
        button.removeClass('error');
        }, RESULT_TIME);
}

$(function() {
    $('.save').click(function() {
        let caller = $(this);
        $.ajax({
            url: '/savePushbulletToken',
            data: $(this).closest('form').serialize(),
            type: 'POST',
            success: function() {
                show_success(caller);
            },
            error: function(xhr, error, errorThrown) {
                if (xhr.status === 400){
                    toast("fill in all the camps correctly: " + xhr.responseText);
                } else {
                    toast("unexpected error, contact support")
                }
                show_error(caller);
            }
        });
    });
});


function toast(text){
    $('.toast').addClass('toast-error').text(text).fadeIn(400).delay(RESULT_TIME).fadeOut(400);
}

$(function() {
    $('.update').click(function() {
        let caller = $(this);
        $.ajax({
            url: '/updatePlan',
            data: $(this).closest('form').serialize()
                + '&' + "arrow="+encodeURI(this.closest('form').arrow.value),
            type: 'POST',
            success: function() {
                show_success(caller);
            },
            error: function(xhr, error, errorThrown) {
                if (xhr.status === 400){
                    toast("fill in all the camps correctly: " + xhr.responseText);
                } else {
                    toast("unexpected error, contact support")
                }
                show_error(caller);
            }
        });
    });
});


$(function() {
    $('.add').click(function() {
        let caller = $(this);
        $.ajax({
            url: '/addPlan',
            data: $(this).closest('form').serialize()
                + '&' + "arrow="+encodeURI(this.closest('form').arrow.value),
            type: 'POST',
            success: function() {
                location.reload();
            },
            error: function(xhr, error, errorThrown) {
                if (xhr.status === 400){
                    toast("fill in all the camps correctly: " + xhr.responseText);
                } else {
                    toast("unexpected error, contact support")
                }
                show_error(caller);
            }
        });
    });
});


$(function() {
    $('.remove').click(function() {
        $.ajax({
            url: '/removePlan',
            data: "idx="+encodeURI(this.closest('form').idx.value),
            type: 'POST',
            success: function(response) {
                $('#remove').addClass('success');
                setTimeout(function () {
                    $('#remove').removeClass('success');
                }, 2000);
                console.log(response);
                location.reload();
            },
            error: function(error) {
                console.log(error);
                $('#remove').addClass('error');
                console.log(error);
                $('.toast').addClass('toast-error').text("could not update plan").fadeIn(400).delay(3000).fadeOut(400);
                setTimeout(function () {
                    $('#remove').removeClass('error');
                }, 2000);
            }
        });
    });
});


$(function() {
    $('.new').click(function() {
        $("html, body").animate({ scrollTop: $(document).height() }, "slow");

        let adder = $('.adder');

        if(adder.is(':visible')){
            adder.addClass("shake-effect");
            setTimeout(function () {
                adder.removeClass("shake-effect");
                }, 820);
        } else {
            adder.hide().fadeTo("fast", 1);
        }
    });
});


$(function() {
    $('.discard').click(function() {
        console.log("clicked");


        $('.adder').fadeTo("fast", 0, function(){
            $("html, body").animate({ scrollTop: 0}, "slow", function () {
                $('.adder').hide();
            });
        });

    });
});

$(function() {
    $('.schedule').click(function() {
        let status = $(this).data('status');
        if (!status || typeof status === 'undefined'){
            $(this).data('status', true);
            $(this).addClass('tile-selected');
            $(this).parent().parent().find('.times').show();
        } else {
            $(this).removeClass('tile-selected');
            $(this).data('status', false);
             $(this).parent().parent().find('.times').hide();
        }
    });
});

$(function() {
    $('.sticky').click(function() {
        let status = $(this).data('status');
        if (!status || typeof status === 'undefined'){
            $(this).addClass('tile-selected');
            $(this).data('status', true);
        } else {
            $(this).removeClass('tile-selected');
            $(this).data('status', false);
        }
    });
});


