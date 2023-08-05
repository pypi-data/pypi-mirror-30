$(document).ready(function() {
    /* Add a [>>>] button on the top-right corner of code samples to hide
     * the >>> and ... prompts and the output and thus make the code
     * copyable. */
    var div = $('.highlight-python .highlight,' +
                '.highlight-pycon .highlight,' +
                '.highlight-python3 .highlight')
    var pre = div.find('pre');

    // get the styles from the current theme
    pre.parent().parent().css('position', 'relative');
    var hide_text = 'Hide the prompts and output';
    var show_text = 'Show the prompts and output';
    var border_width = pre.css('border-top-width');
    var border_style = pre.css('border-top-style');
    var border_color = pre.css('border-top-color');
    var button_styles = {
        'cursor':'pointer', 'position': 'absolute', 'top': '0', 'right': '0',
        'border-color': border_color, 'border-style': border_style,
        'border-width': border_width, 'color': '#666666', 'text-size': '75%',
        'font-family': 'monospace', 'padding-left': '0.2em', 'padding-right': '0.2em',
        'border-radius': '0 3px 0 0'
    }

    // create and add the button to all the code blocks that contain >>>
    div.each(function(index) {
        var jthis = $(this);
        if (jthis.find('.gp').length > 0) {
            var button = $('<span class="copybutton">&gt;&gt;&gt;</span>');
            button.css(button_styles)
            button.attr('title', hide_text);
            jthis.prepend(button);
        }
        // tracebacks (.gt) contain bare text elements that need to be
        // wrapped in a span to work with .nextUntil() (see later)
        jthis.find('pre:has(.gt)').contents().filter(function() {
            return ((this.nodeType == 3) && (this.data.trim().length > 0));
        }).wrap('<span>');
        // completely hide output lines by moving the newline
        // into the <pre class='go'> elements
        jthis.find('pre:has(.go)').each(function() {
            var pre = $(this);
            pre.find('.go').each(function () {
                var prev = $(this.previousSibling);
                var prev_text = prev.text();
                if (prev_text[0] == '\n') {
                    prev.remove();
                    $(this).prepend(prev_text);
                } else {
                    $(this).prepend('\n');
                }
            });
            // handle highlighted lines
            pre.find('.hll').each(function () {
                if ($(this).next().attr("class") == "go") {
                    var t = $(this).html().replace(/\n$/i,'');
                    $(this).html(t);
                }
            });
        });
    });

    // define the behavior of the button when it's clicked
    $('.copybutton').click(function () {
        var button = $(this);
        if (button.css('text-decoration') == 'line-through') {
            button.parent().find('.go, .gp, .gt').show();
            button.next('pre').find('.gt').nextUntil('.gp, .go').css('visibility', 'visible');
            button.css('text-decoration', 'none');
            button.attr('title', hide_text);
        } else {
            button.parent().find('.go, .gp, .gt').hide();
            button.next('pre').find('.gt').nextUntil('.gp, .go').css('visibility', 'hidden');
            button.css('text-decoration', 'line-through');
            button.attr('title', show_text);
        }
    });
});
