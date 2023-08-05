'use strict';

(function () {

    var entryTemplate = _.template('<li class="list-edit-entry" data-list-index="<%- index %>">\n <input type="text"<%= inputAttrs %>>\n <a href="#" class="list-edit-remove-item" role="button"\n    title=<%- removeText %>">\n   <img src="<%- deleteImgUrl %>">\n </a>\n</li>');

    /**
     * A view for editing a list of elements.
     *
     * This is the JavaScript view for
     * :py:class:`djblets.forms.widgets.ListEditWidget`.
     */
    Djblets.Forms.ListEditView = Backbone.View.extend({
        events: {
            'click .list-edit-add-item': '_addItem',
            'click .list-edit-remove-item': '_removeItem',
            'blur input': '_onBlur'
        },

        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         The view options.
         *
         * Option Args:
         *     inputAttrs (string):
         *         The attributes that should be added to each ``<input>`` element.
         *
         *     deleteImgUrl (string):
         *         The URL for the delete icon image.
         *
         *     removeText (string):
         *         The localized text for removing an item.
         *
         *     sep (string):
         *         The list separator. It will be used to join the list of values
         *         into a string.
         */
        initialize: function initialize(options) {
            this._inputAttrs = options.inputAttrs;
            this._deleteImgUrl = options.deleteImgUrl;
            this._removeText = options.removeText;
            this._sep = options.sep;
            this._values = [];
        },


        /**
         * Render the view.
         *
         * Since most of the view is rendered by Django, this just sets up some
         * event listeners.
         *
         * Returns:
         *     Djblets.Forms.ListEditView:
         *     This view.
         */
        render: function render() {
            var _this = this;

            this._$list = this.$('ul');
            this._$list.find('.list-edit-entry > input').each(function (idx, el) {
                _this._values.push($(el).val());
            });
            this._$addBtn = this.$('.list-edit-add-item');
            this._$hidden = this.$('input[type="hidden"]');

            return this;
        },


        /**
         * Remove the view from the DOM.
         *
         * Returns:
         *     Djblets.Forms.ListEditView:
         *     This view.
         */
        remove: function remove() {
            this.$el.closest('form').off('submit', this._onSubmit);
            return this;
        },


        /**
         * Add an item to the list.
         *
         * Args:
         *     e (Event):
         *         The click event that triggered this event handler.
         */
        _addItem: function _addItem(e) {
            var _this2 = this;

            e.preventDefault();
            e.stopPropagation();

            var $entry = $(entryTemplate({
                index: this._values.length,
                deleteImgUrl: this._deleteImgUrl,
                inputAttrs: this._inputAttrs,
                removeText: this._removeText
            })).insertBefore(this._$addBtn);

            $entry.find('.list-edit-add-item').on('click', function (e) {
                return _this2._addItem(e);
            }).end().find('input').on('change', function (e) {
                return _this2._onBlur(e);
            }).end();

            this._values.push('');
        },


        /**
         * Remove an item.
         *
         * When there is only a single item in the list, we clear it instead of
         * removing it so there is always at least one ``<input>`` element and
         * value in the list.
         *
         * Args:
         *     e (Event):
         *         The click event that triggered this event handler.
         */
        _removeItem: function _removeItem(e) {
            e.preventDefault();
            e.stopPropagation();

            var $target = $(e.target);
            var $entry = $target.closest('.list-edit-entry');
            var index = $entry.attr('data-list-index');

            if (this._values.length > 1) {
                $entry.remove();
                this._values.splice(index, 1);
                this._$list.find('.list-edit-entry').each(function (idx, el) {
                    $(el).attr('data-list-index', idx);
                });
            } else {
                this._values[index] = '';
                $target.siblings('input').val('');
            }

            this._$hidden.val(this._values.filter(function (v) {
                return v.length > 0;
            }).join(this._sep));
        },


        /**
         * Update the internal values when a field changes.
         *
         * Args:
         *     e (Event):
         *         The blur event.
         */
        _onBlur: function _onBlur(e) {
            var $target = $(e.target);
            var index = $target.closest('.list-edit-entry').attr('data-list-index');

            this._values[index] = $target.val();
            this._$hidden.val(this._values.filter(function (v) {
                return v.length > 0;
            }).join(this._sep));
        }
    });
})();

//# sourceMappingURL=listEditView.js.map