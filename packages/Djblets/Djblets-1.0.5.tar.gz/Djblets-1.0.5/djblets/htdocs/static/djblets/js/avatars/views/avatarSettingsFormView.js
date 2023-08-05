'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

(function () {
    var _Promise$withResolver = Promise.withResolver(),
        _Promise$withResolver2 = _slicedToArray(_Promise$withResolver, 2),
        readyPromise = _Promise$withResolver2[0],
        resolve = _Promise$withResolver2[1];

    /**
     * A form for managing the settings of avatar services.
     *
     * This form lets you select the avatar service you wish to use, as well as
     * configure the settings for that avatar service.
     */


    Djblets.Avatars.SettingsFormView = Backbone.View.extend({
        events: {
            'change #id_avatar_service_id': '_onServiceChanged',
            'submit': '_onSubmit'
        },

        /**
         * Initialize the form.
         */
        initialize: function initialize() {
            var _this = this;

            console.assert(Djblets.Avatars.SettingsFormView.instance === null);
            Djblets.Avatars.SettingsFormView.instance = this;
            this._configForms = new Map();

            this._$config = this.$('.avatar-service-configuration');

            var services = this.model.get('services');
            this.listenTo(this.model, 'change:serviceID', function () {
                return _this._showHideForms();
            });

            /*
             * The promise continuations will only be executed once the stack is
             * unwound.
             */
            resolve();
        },


        /**
         * Validate the current form upon submission.
         *
         * Args:
         *     e (Event):
         *         The form submission event.
         */
        _onSubmit: function _onSubmit(e) {
            var serviceID = this.model.get('serviceID');
            var currentForm = this._configForms.get(serviceID);

            if (currentForm && !currentForm.validate()) {
                e.preventDefault();
            }
        },


        /**
         * Render the child forms.
         *
         * This will show the for the currently selected service if it has one.
         *
         * Returns:
         *     Djblets.Avatars.SettingsFormView:
         *     This view (for chaining).
         */
        renderForms: function renderForms() {
            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = this._configForms.values()[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    var form = _step.value;

                    form.render();
                }

                /*
                 * Ensure that if the browser sets the value of the <select> upon
                 * refresh that we update the model accordingly.
                 */
            } catch (err) {
                _didIteratorError = true;
                _iteratorError = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion && _iterator.return) {
                        _iterator.return();
                    }
                } finally {
                    if (_didIteratorError) {
                        throw _iteratorError;
                    }
                }
            }

            this.$('#id_avatar_service_id').change();
            this._showHideForms(true);

            return this;
        },


        /**
         * Show or hide the configuration form.
         */
        _showHideForms: function _showHideForms() {
            var services = this.model.get('services');
            var serviceID = this.model.get('serviceID');
            var currentForm = this._configForms.get(serviceID);
            var previousID = this.model.previous('serviceID');
            var previousForm = previousID ? this._configForms.get(previousID) : undefined;

            if (previousForm && currentForm) {
                previousForm.$el.hide();
                currentForm.$el.show();
            } else if (previousForm) {
                previousForm.$el.hide();
                this._$config.hide();
            } else if (currentForm) {
                currentForm.$el.show();
                this._$config.show();
            }
        },


        /**
         * Handle the service being changed.
         *
         * Args:
         *     e (Event):
         *         The change event.
         */
        _onServiceChanged: function _onServiceChanged(e) {
            var $target = $(e.target);
            this.model.set('serviceID', $target.val());
        }
    }, {
        /**
         * The form instance.
         */
        instance: null,

        /**
         * Add a configuration form to the instance.
         *
         * Args:
         *     serviceID (string):
         *         The unique ID for the avatar service.
         *
         *     formClass (constructor):
         *         The view to use for the form.
         */
        addConfigForm: function addConfigForm(serviceID, formClass) {
            Djblets.Avatars.SettingsFormView.instance._configForms.set(serviceID, new formClass({
                el: $('[data-avatar-service-id="' + serviceID + '"]'),
                model: Djblets.Avatars.SettingsFormView.instance.model
            }));
        },


        /**
         * A promise that is resolved when the avatar services form has been
         * initialized.
         */
        ready: readyPromise
    });
})();

//# sourceMappingURL=avatarSettingsFormView.js.map