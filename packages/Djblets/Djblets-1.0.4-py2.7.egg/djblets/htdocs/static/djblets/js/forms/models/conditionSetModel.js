'use strict';

/**
 * A set of configured conditions, and available choices.
 *
 * This tracks all the conditions that are being configured, handling assigning
 * each one an ID and tracking their state. It also provides information on
 * each choice available for a condition.
 *
 * Attributes:
 *     choices (Backbone.Collection):
 *         A collection of possible choices for a condition. Each entry is a
 *         :js:class:`Djblets.Forms.ConditionChoice`.
 *
 *     conditions (Backbone.Collection):
 *         A collection of configured conditions. Each entry is a
 *         :js:class:`Djblets.Forms.Condition`.
 *
 * Model Attributes:
 *     fieldName (string):
 *         The name of the form field for the main conditions element.
 *
 *     lastID (number):
 *         The last condition row ID used.
 */
Djblets.Forms.ConditionSet = Backbone.Model.extend({
    defaults: {
        fieldName: null,
        lastID: null
    },

    /**
     * Initialize the model.
     *
     * Args:
     *     attributes (object):
     *         Attribute values passed to the constructor.
     */
    initialize: function initialize(attributes) {
        var _this = this;

        this.choices = new Backbone.Collection(attributes.choicesData, {
            model: Djblets.Forms.ConditionChoice,
            parse: true
        });

        this.conditions = new Backbone.Collection(attributes.conditionsData, {
            model: function model(attrs, options) {
                var choice = attrs.choice || _this.choices.get(attrs.choiceID);
                var operator = attrs.operator || (choice ? choice.operators.get(attrs.operatorID) : null);
                var lastID = _this.get('lastID');
                var conditionID = lastID === null ? 0 : lastID + 1;

                _this.set('lastID', conditionID);

                return new Djblets.Forms.Condition({
                    id: conditionID,
                    choice: choice,
                    operator: operator,
                    value: attrs.value,
                    valid: attrs.valid,
                    error: attrs.error
                }, options);
            }
        });
    },


    /**
     * Add a new condition.
     *
     * This will construct a new condition with defaults and add it to the
     * collection.
     */
    addNewCondition: function addNewCondition() {
        var choice = this.choices.first();

        this.conditions.add({
            choice: choice,
            operator: choice.operators.first()
        });
    },


    /**
     * Parse the attribute data passed to the model.
     *
     * This will extract only the ``fieldName`` attribute, leaving the rest
     * to be specially handled by :js:func:`initialize`.
     *
     * Args:
     *     data (object):
     *         The attribute data passed to the model.
     *
     * Returns:
     *     object:
     *     The parsed attributes.
     */
    parse: function parse(data) {
        return {
            fieldName: data.fieldName
        };
    }
});

//# sourceMappingURL=conditionSetModel.js.map