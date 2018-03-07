$(function() {

    $.widget("custom.quantity", {
        options: {
            id: 0,
            quantity: 0,
            delta: 0,

            validator: function(_v) {
                return true;
            },
            validator_err: "",

            _state: {},
        },

        _state: {},

        _adjust:  function(f, e) {
            var s = this.options._state;
            var newval = f(parseInt(s.delta.val()));
            var curval = parseInt(s.prev.html()) + newval;
            if (this.options.validator(newval) && curval >= 0) {
                s.delta.val(newval);
                s.curval = curval;
                this.refresh();
            }
        },

        _create: function() {

            /*
              Change type of original text field to hidde
              Create new text field which displays the delta
              Insert full element including new structure adjacent
              to old element
            */

            var o = this.options;
            var s = o._state;
            var block = $('<div class="flex flex-column">\
<div>Før: <span class="prev-qty"></span></div>\
<div class="clearfix border" style="width: 141px">\
<button type="button" class="minus btn">-</button>\
<input type="text" value="0" class="delta qfield field ml2" />\
<button type="button" class="plus btn">+</button>\
</div>\
<div>Efter: <span class="new-qty"></span></div>\
</div>');

            s.minus = $(".minus", block);
            s.plus = $(".plus", block);
            s.delta = $('.delta', block);
            s.prev = $('.prev-qty', block);
            s.cur = $('.new-qty', block);

            s.curval = parseInt(this.element.data("curval"));
            s.prevval = s.curval;
            s.prev.html(s.curval);

            // Set old formfield to hidden
            this.element.attr("type", "hidden")
            this.options.quantity = parseInt(this.element.attr("value"));
            this.element.after(block);

            s.minus.on("click touchstart", this, function(event) {
                event.data._adjust(function(v) {return v - 1;},
                                   event.data);
                event.preventDefault();
            });
            s.plus.on("click touchstart", this, function(event) {
                event.data._adjust(function(v) {return v + 1;},
                                   event.data);
                event.preventDefault();
            });
            s.delta.on("keyup", this, function(event) {
                event.data._adjust(function(v) {return v;},
                                   event.data);
            });
            s.delta.on("blur", this, function(event) {
                var s = event.data.options._state;
                var curdelta = parseInt(s.delta.val());
                s.delta.val(s.curval - s.prevval);
            });
            s.delta.on("click", this, function(event) {
                $(this).select();
            });
            this.refresh();
        },

        refresh: function() {
            var s = this.options._state;
            s.cur.html(s.curval)
            this.element.val(s.curval);
            if(s.prevval !== s.curval) {
                s.delta.closest("tr").addClass("trHighlight");
            } else {``
                s.delta.closest("tr").removeClass("trHighlight");
            }

        }});
});
