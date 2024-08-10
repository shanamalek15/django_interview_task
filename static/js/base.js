$(function(){

        var currentPath = window.location.pathname;
        $('.nav-link').each(function() {
            if ($(this).data('url') === currentPath) {
                $(this).addClass('active');
            }
        });
})