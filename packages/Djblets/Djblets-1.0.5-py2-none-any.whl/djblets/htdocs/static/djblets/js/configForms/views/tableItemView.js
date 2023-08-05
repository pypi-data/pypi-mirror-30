'use strict';

/**
 * Renders a ListItem as a row in a table.
 *
 * This is meant to be used with TableView. Subclasses will generally want
 * to override the template.
 */
Djblets.Config.TableItemView = Djblets.Config.ListItemView.extend({
    tagName: 'tr',

    template: _.template('<td>\n<% if (editURL) { %>\n<a href="<%- editURL %>"><%- text %></a>\n<% } else { %>\n<%- text %>\n<% } %>\n</td>'),

    /**
     * Return the container for the actions.
     *
     * This defaults to being the last cell in the row, but this can be
     * overridden to provide a specific cell or an element within.
     *
     * Returns:
     *     jQuery:
     *     The element where actions should be rendered.
     */
    getActionsParent: function getActionsParent() {
        return this.$('td:last');
    }
});

//# sourceMappingURL=tableItemView.js.map