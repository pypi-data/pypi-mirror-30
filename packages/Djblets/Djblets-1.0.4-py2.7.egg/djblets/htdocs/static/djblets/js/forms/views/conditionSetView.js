'use strict';

(function () {

    /**
     * Base view for condition rows.
     *
     * This is responsible for handling common logic for condition row views. It's
     * mainly used to handle deletion of the row.
     */
    var BaseConditionRowView = Backbone.View.extend({
        tagName: 'li',
        className: 'conditions-field-row',

        events: {
            'click .conditions-field-row-delete': '_onDeleteClicked'
        },

        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         Options for the view.
         *
         * Option Args:
         *     rowAnimationSpeedMS (number):
         *         The animation speed for adding/removing rows.
         */
        initialize: function initialize(options) {
            var _this = this;

            this.listenTo(this.model, 'destroy', function () {
                _this.$el.slideUp(options.rowAnimationSpeedMS, _this.remove.bind(_this));
            });
        },


        /**
         * Callback for when the delete button is clicked.
         *
         * Deletes the model, which will in turn delete this row.
         */
        _onDeleteClicked: function _onDeleteClicked(e) {
            e.stopPropagation();
            e.preventDefault();

            this.model.destroy();
        }
    });

    /**
     * A view representing a row containing a choice, operator, and value.
     *
     * This is responsible for allowing a user to choose the values for one
     * condition. Choosing a choice will populate a list of operators, and choosing
     * an operator will show or hide a value field (depending on the operator).
     */
    var ConditionRowView = BaseConditionRowView.extend({
        template: _.template(['<span class="conditions-field-action conditions-field-row-delete">\n', ' <span class="fa fa-minus-circle"></span>\n', '</span>\n', '<span class="conditions-field-row-options">\n', ' <% if (error) { %>', '  <ul class="error-list"><li><%- error %></li></ul>\n', ' <% } %>', ' <span class="conditions-field-choice"></span>\n', ' <span class="conditions-field-operator"></span>\n', ' <span class="conditions-field-value"></span>\n', '</span>'].join('')),

        events: _.extend({
            'change .conditions-field-choice select': '_onSelectChoiceChanged',
            'change .conditions-field-operator select': '_onSelectOperatorChanged'
        }, BaseConditionRowView.prototype.events),

        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         Options for the view.
         *
         * Option Args:
         *     conditionSet (Djblets.Forms.ConditionSet):
         *         The condition set defining the choices allowed. This is
         *         required.
         *
         *     rowAnimationSpeedMS (number):
         *         The animation speed for adding/removing rows.
         */
        initialize: function initialize(options) {
            BaseConditionRowView.prototype.initialize.call(this, options);

            this.conditionSet = options.conditionSet;

            this._$choice = null;
            this._$operator = null;
            this._$valueWrapper = null;
            this._$newValue = null;
            this._defaultValueField = null;
            this._valueField = null;
        },


        /**
         * Render the view.
         *
         * This will create and populate the choice, operator and value fields,
         * based on the contents of the model, and begin listening to events.
         *
         * Returns:
         *     ConditionRowView:
         *     The instance, for chaining.
         */
        render: function render() {
            var _this2 = this;

            this.$el.html(this.template(this.model.attributes));

            var $rowOptions = this.$el.children('.conditions-field-row-options');
            var fieldName = this.conditionSet.get('fieldName');
            var rowNum = this.model.get('id');

            /* Build the list of choices. This will be populated up-front. */
            this._$choice = $('<select/>').attr('name', fieldName + '_choice[' + rowNum + ']');

            this.conditionSet.choices.each(function (choice) {
                _this2._$choice.append($('<option/>').val(choice.id).text(choice.get('name')));
            });

            this._$choice.appendTo($rowOptions.children('.conditions-field-choice'));

            /*
             * Build the list for the operators. This will be populated when
             * calling _onChoiceChanged, and whenever the choice changes.
             */
            this._$operator = $('<select/>').attr('name', fieldName + '_operator[' + rowNum + ']').appendTo($rowOptions.children('.conditions-field-operator'));

            this._$valueWrapper = $rowOptions.children('.conditions-field-value');

            /*
             * Bind all the events so the attributes and inputs reflect each other.
             * We'll also be binding visibility.
             */
            this.listenTo(this.model, 'change:choice', this._onChoiceChanged);
            this.listenTo(this.model, 'change:operator', this._onOperatorChanged);
            this.listenTo(this.model, 'change:value', this._onValueChanged);

            /* Set the initial state for the choice and operator from the model. */
            this._onChoiceChanged();
            this._onOperatorChanged();
            this._onValueChanged();

            return this;
        },


        /**
         * Callback for when the choice attribute changes on the model.
         *
         * Updates the list of operators and sets up a new field for the value,
         * getting rid of the old one.
         */
        _onChoiceChanged: function _onChoiceChanged() {
            var _this3 = this;

            var choice = this.model.get('choice');
            var fieldName = this.conditionSet.get('fieldName');
            var rowNum = this.model.get('id');

            this._$choice.val(choice.id);

            this._defaultValueField = choice.createValueField(fieldName + '_value[' + rowNum + ']');

            /* Rebuild the list of operators for the choice. */
            this._$operator.empty();

            choice.operators.each(function (operator) {
                _this3._$operator.append($('<option/>').val(operator.id).text(operator.get('name')));
            });

            this._$operator.val(this.model.get('operator').id);
        },


        /**
         * Callback for when the operator changes on the model.
         *
         * Updates the visibility of the value, based on whether the operator
         * needs one.
         */
        _onOperatorChanged: function _onOperatorChanged() {
            var operator = this.model.get('operator');
            var newValueField = void 0;

            this._$operator.val(operator.id);
            this._$valueWrapper.setVisible(operator.get('useValue'));

            if (operator.get('valueField') !== null) {
                var fieldName = this.conditionSet.get('fieldName');
                var rowNum = this.model.get('id');

                newValueField = operator.createValueField(fieldName + '_value[' + rowNum + ']');
            } else {
                newValueField = this._defaultValueField;
            }

            if (newValueField !== this._valueField) {
                /* Replace the old value field with a new one for this choice. */
                if (this._$newValue !== null && newValueField !== this._valueField) {
                    this._$newValue.remove();
                    this._$newValue = null;
                }

                this._valueField = newValueField;

                this._$newValue = this._valueField.render().$el.appendTo(this._$valueWrapper);
            }
        },


        /**
         * Callback for when the value changes on the model.
         *
         * Updates the field to reflect the new value.
         */
        _onValueChanged: function _onValueChanged() {
            this._valueField.setValue(this.model.get('value'));
        },


        /**
         * Callback for when a new condition choice is chosen in the drop-down.
         *
         * Updates the choice in the model.
         */
        _onSelectChoiceChanged: function _onSelectChoiceChanged() {
            this.model.set('choice', this.conditionSet.choices.get(this._$choice.val()));
        },


        /**
         * Callback for when a new operator is chosen in the drop-down.
         *
         * Updates the operator in the model.
         */
        _onSelectOperatorChanged: function _onSelectOperatorChanged() {
            var choice = this.model.get('choice');

            this.model.set('operator', choice.operators.get(this._$operator.val()));
        }
    });

    /**
     * A view representing a disabled condition row.
     *
     * This is used for conditions that are considered invalid (ones whose choice
     * or operator could not be found when loading). The condition is shown in a
     * disabled state, with the raw value alongside it (if set). It can only be
     * removed.
     */
    var DisabledConditionRowView = BaseConditionRowView.extend({
        render: function render() {
            var value = this.model.get('value');

            if (value !== null) {
                this.$('.conditions-field-value').text(value);
            }

            return this;
        }
    });

    /**
     * A view for creating, editing, and deleting a set of conditions.
     *
     * This starts off by listing all the conditions already configured (as
     * represented by the data in the associated model), and allows those
     * conditions to be edited/deleted or new ones to be created.
     *
     * Options:
     *     rowAnimationSpeedMS (number):
     *         The animation speed (in milliseconds) for adding or removing
     *         condition rows.
     */
    Djblets.Forms.ConditionSetView = Backbone.View.extend({
        DEFAULT_ROW_ANIMATION_SPEED_MS: 300,

        events: {
            'click .conditions-field-add-condition': '_onAddRowClicked',
            'change #conditions_mode input': '_onConditionModeChanged'
        },

        /**
         * Initialize the view.
         */
        initialize: function initialize(options) {
            this._rowAnimationSpeedMS = options.rowAnimationSpeedMS || this.DEFAULT_ROW_ANIMATION_SPEED_MS;

            this._$lastID = null;
            this._$rows = null;
        },


        /**
         * Render the view.
         *
         * This will construct a :js:class:`ConditionRowView` for each condition
         * that has been provided, and hook up events to handle the creation or
         * deletion of conditions.
         *
         * Returns:
         *     Djblets.Forms.ConditionSetView:
         *     This instance, for chaining.
         */
        render: function render() {
            var _this4 = this;

            var fieldName = this.model.get('fieldName');
            var conditions = this.model.conditions;

            this._$lastID = this.$el.children('input[name=' + fieldName + '_last_id]').bindProperty('value', this.model, 'lastID');
            this._$mode = this.$('#conditions_mode input');
            this._$rowsContainer = this.$('.conditions-field-rows-container');
            this._$rows = this._$rowsContainer.children('.conditions-field-rows');

            /* Render rows for any existing conditions. */
            var $rowItems = this._$rows.children();

            conditions.each(function (condition, i) {
                _this4._addConditionRow(condition, $rowItems[i]);
            });

            /* Begin listening for any events that impact the rows or inputs. */
            this.listenTo(conditions, 'add', function (condition) {
                return _this4._addConditionRow(condition);
            });

            this._onConditionModeChanged();

            return this;
        },


        /**
         * Add a condition row to the UI.
         *
         * This is called when a new condition has been added in the models. It
         * constructs a :js:class:`ConditionRowView` and renders it in the list.
         *
         * Args:
         *     condition (Djblets.Forms.Condition):
         *         The condition being added.
         *
         *     $rowEl (jQuery):
         *         The element to use for the row. If not provided, a new one
         *         will be created.
         */
        _addConditionRow: function _addConditionRow(condition, $rowEl) {
            var RowViewCls = condition.get('valid') ? ConditionRowView : DisabledConditionRowView;

            var rowView = new RowViewCls({
                conditionSet: this.model,
                el: $rowEl,
                model: condition,
                rowAnimationSpeedMS: this._rowAnimationSpeedMS
            });
            rowView.render();

            if ($rowEl === undefined) {
                rowView.$el.hide().appendTo(this._$rows).slideDown(this._rowAnimationSpeedMS);
            }
        },


        /**
         * Handler for when "Add a new condition" is clicked.
         *
         * This adds a new condition to the model, which will in turn render the
         * new row to the list.
         *
         * Args:
         *     e (Event):
         *         The click event.
         */
        _onAddRowClicked: function _onAddRowClicked(e) {
            e.stopPropagation();
            e.preventDefault();

            this.model.addNewCondition();
        },


        /**
         * Handler for when the condition mode changes.
         *
         * If the current mode is "Always", hide the conditions list.
         */
        _onConditionModeChanged: function _onConditionModeChanged() {
            var mode = this._$mode.filter(':checked').val();

            this._$rowsContainer.setVisible(mode !== 'always');
        }
    });
})();

//# sourceMappingURL=conditionSetView.js.map