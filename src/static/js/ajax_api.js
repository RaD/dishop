$(document).ready(function () {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                              }
        }
        return cookieValue;
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

	$('#add_to_cart').removeAttr('onclick');

	$('#add_to_cart').click(function () {
		$.ajax({
			type: 'post',
			url: '/shop/cart/add/',
			dataType: 'html',
			data: $('#product :input'),
			success: function (html) {
				$('#module_cart .middle').html(html);
			},
			complete: function () {
				var image = $('#image').offset();
				var cart  = $('#module_cart').offset();

				$('#image').before('<img src="' + $('#image').attr('src')
                                                + '" id="temp" style="position: absolute; top: '
                                                + image.top + 'px; left: ' + image.left + 'px;" />');

				params = {
					top : cart.top + 'px',
					left : cart.left + 'px',
					opacity : 0.0,
					width : $('#module_cart').width(),
					height : $('#module_cart').height()
				};

				$('#temp').animate(params, 'slow', false, function () {
					$('#temp').remove();
				});
			}
		});
	});

	$('.cart_remove').live('click', function () {
		if (!confirm(ARE_YOU_SURE)) {
			return false;
		}
		$(this).removeClass('cart_remove').addClass('cart_remove_loading');
		$.ajax({
			type: 'post',
			url: '/shop/cart/del/',
			dataType: 'html',
			data: 'product_id=' + this.id,
			success: function (html) {
				$('#module_cart .middle').html(html);
			}
		});
	});
});
