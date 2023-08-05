'use strict';

suite('djblets/configForms/views/ListItemView', function () {
    describe('Rendering', function () {
        describe('Item display', function () {
            it('With editURL', function () {
                var item = new Djblets.Config.ListItem({
                    editURL: 'http://example.com/',
                    text: 'Label'
                });
                var itemView = new Djblets.Config.ListItemView({
                    model: item
                });

                itemView.render();
                expect(itemView.$el.html().strip()).toBe(['<span class="config-forms-list-item-actions"></span>', '<a href="http://example.com/">Label</a>'].join('\n'));
            });

            it('Without editURL', function () {
                var item = new Djblets.Config.ListItem({
                    text: 'Label'
                });
                var itemView = new Djblets.Config.ListItemView({
                    model: item
                });

                itemView.render();
                expect(itemView.$el.html().strip()).toBe(['<span class="config-forms-list-item-actions"></span>', 'Label'].join('\n'));
            });
        });

        describe('Actions', function () {
            it('Checkboxes', function () {
                var item = new Djblets.Config.ListItem({
                    text: 'Label',
                    checkboxAttr: false,
                    actions: [{
                        id: 'mycheckbox',
                        type: 'checkbox',
                        label: 'Checkbox',
                        propName: 'checkboxAttr'
                    }]
                });
                var itemView = new Djblets.Config.ListItemView({
                    model: item
                });

                itemView.render();

                expect(itemView.$('input[type=checkbox]').length).toBe(1);
                expect(itemView.$('label').length).toBe(1);
            });

            describe('Buttons', function () {
                it('Simple', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        actions: [{
                            id: 'mybutton',
                            label: 'Button'
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $button = itemView.$('.btn');
                    expect($button.length).toBe(1);
                    expect($button.text()).toBe('Button');
                    expect($button.hasClass('config-forms-list-action-mybutton')).toBe(true);
                    expect($button.hasClass('rb-icon')).toBe(false);
                    expect($button.hasClass('danger')).toBe(false);
                });

                it('Danger', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        actions: [{
                            id: 'mybutton',
                            label: 'Button',
                            danger: true
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $button = itemView.$('.btn');
                    expect($button.length).toBe(1);
                    expect($button.text()).toBe('Button');
                    expect($button.hasClass('config-forms-list-action-mybutton')).toBe(true);
                    expect($button.hasClass('rb-icon')).toBe(false);
                    expect($button.hasClass('danger')).toBe(true);
                });

                it('Icon names', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        actions: [{
                            id: 'mybutton',
                            label: 'Button',
                            danger: false,
                            iconName: 'foo'
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $button = itemView.$('.btn');
                    expect($button.length).toBe(1);
                    expect($button.text()).toBe('Button');
                    expect($button.hasClass('config-forms-list-action-mybutton')).toBe(true);
                    expect($button.hasClass('danger')).toBe(false);

                    var $span = $button.find('span');
                    expect($span.length).toBe(1);
                    expect($span.hasClass('djblets-icon')).toBe(true);
                    expect($span.hasClass('djblets-icon-foo')).toBe(true);
                });
            });

            describe('Menus', function () {
                var item = void 0;
                var itemView = void 0;

                beforeEach(function () {
                    item = new Djblets.Config.ListItem({
                        text: 'Label',
                        actions: [{
                            id: 'mymenu',
                            label: 'Menu',
                            children: [{
                                id: 'mymenuitem',
                                label: 'My menu item'
                            }]
                        }]
                    });

                    itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();
                });

                it('Initial display', function () {
                    var $button = itemView.$('.btn');

                    expect($button.length).toBe(1);
                    expect($button.text()).toBe('Menu ▾');
                });

                it('Opening', function () {

                    /* Prevent deferring. */
                    spyOn(_, 'defer').and.callFake(function (cb) {
                        cb();
                    });

                    spyOn(itemView, 'trigger');

                    var $action = itemView.$('.config-forms-list-action-mymenu');
                    $action.click();

                    var $menu = itemView.$('.action-menu');
                    expect($menu.length).toBe(1);
                    expect(itemView.trigger.calls.mostRecent().args[0]).toBe('actionMenuPopUp');
                });

                it('Closing', function () {
                    /* Prevent deferring. */
                    spyOn(_, 'defer').and.callFake(function (cb) {
                        return cb();
                    });

                    var $action = itemView.$('.config-forms-list-action-mymenu');
                    $action.click();

                    spyOn(itemView, 'trigger');
                    $(document.body).click();

                    expect(itemView.trigger.calls.mostRecent().args[0]).toBe('actionMenuPopDown');

                    var $menu = itemView.$('.action-menu');
                    expect($menu.length).toBe(0);
                });
            });
        });

        describe('Action properties', function () {
            describe('enabledPropName', function () {
                it('value == undefined', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        actions: [{
                            id: 'mycheckbox',
                            type: 'checkbox',
                            label: 'Checkbox',
                            enabledPropName: 'isEnabled'
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $action = itemView.$('.config-forms-list-action-mycheckbox');

                    expect($action.prop('disabled')).toBe(true);
                });

                it('value == true', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        isEnabled: true,
                        actions: [{
                            id: 'mycheckbox',
                            type: 'checkbox',
                            label: 'Checkbox',
                            enabledPropName: 'isEnabled'
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $action = itemView.$('.config-forms-list-action-mycheckbox');

                    expect($action.prop('disabled')).toBe(false);
                });

                it('value == false', function () {
                    var item = new Djblets.Config.ListItem({
                        text: 'Label',
                        isEnabled: false,
                        actions: [{
                            id: 'mycheckbox',
                            type: 'checkbox',
                            label: 'Checkbox',
                            enabledPropName: 'isEnabled'
                        }]
                    });
                    var itemView = new Djblets.Config.ListItemView({
                        model: item
                    });

                    itemView.render();

                    var $action = itemView.$('.config-forms-list-action-mycheckbox');

                    expect($action.prop('disabled')).toBe(true);
                });

                describe('with enabledPropInverse == true', function () {
                    it('value == undefined', function () {
                        var item = new Djblets.Config.ListItem({
                            text: 'Label',
                            actions: [{
                                id: 'mycheckbox',
                                type: 'checkbox',
                                label: 'Checkbox',
                                enabledPropName: 'isDisabled',
                                enabledPropInverse: true
                            }]
                        });
                        var itemView = new Djblets.Config.ListItemView({
                            model: item
                        });

                        itemView.render();

                        var $action = itemView.$('.config-forms-list-action-mycheckbox');

                        expect($action.prop('disabled')).toBe(false);
                    });

                    it('value == true', function () {
                        var item = new Djblets.Config.ListItem({
                            text: 'Label',
                            isDisabled: true,
                            actions: [{
                                id: 'mycheckbox',
                                type: 'checkbox',
                                label: 'Checkbox',
                                enabledPropName: 'isDisabled',
                                enabledPropInverse: true
                            }]
                        });
                        var itemView = new Djblets.Config.ListItemView({
                            model: item
                        });

                        itemView.render();

                        var $action = itemView.$('.config-forms-list-action-mycheckbox');

                        expect($action.prop('disabled')).toBe(true);
                    });

                    it('value == false', function () {
                        var item = new Djblets.Config.ListItem({
                            text: 'Label',
                            isDisabled: false,
                            actions: [{
                                id: 'mycheckbox',
                                type: 'checkbox',
                                label: 'Checkbox',
                                enabledPropName: 'isDisabled',
                                enabledPropInverse: true
                            }]
                        }),
                            itemView = new Djblets.Config.ListItemView({
                            model: item
                        }),
                            $action;

                        itemView.render();

                        $action = itemView.$('.config-forms-list-action-mycheckbox');

                        expect($action.prop('disabled')).toBe(false);
                    });
                });
            });
        });
    });

    describe('Action handlers', function () {
        it('Buttons', function () {
            var item = new Djblets.Config.ListItem({
                text: 'Label',
                actions: [{
                    id: 'mybutton',
                    label: 'Button'
                }]
            });
            var itemView = new Djblets.Config.ListItemView({
                model: item
            });

            itemView.actionHandlers = {
                mybutton: '_onMyButtonClick'
            };
            itemView._onMyButtonClick = function () {};
            spyOn(itemView, '_onMyButtonClick');

            itemView.render();

            var $button = itemView.$('.btn');
            expect($button.length).toBe(1);
            $button.click();

            expect(itemView._onMyButtonClick).toHaveBeenCalled();
        });

        it('Checkboxes', function () {
            var item = new Djblets.Config.ListItem({
                text: 'Label',
                checkboxAttr: false,
                actions: [{
                    id: 'mycheckbox',
                    type: 'checkbox',
                    label: 'Checkbox',
                    propName: 'checkboxAttr'
                }]
            });
            var itemView = new Djblets.Config.ListItemView({
                model: item
            });

            itemView.actionHandlers = {
                mybutton: '_onMyButtonClick'
            };
            itemView._onMyButtonClick = function () {};
            spyOn(itemView, '_onMyButtonClick');

            itemView.render();

            var $checkbox = itemView.$('input[type=checkbox]');
            expect($checkbox.length).toBe(1);
            expect($checkbox.prop('checked')).toBe(false);
            $checkbox.prop('checked', true).triggerHandler('change');

            expect(item.get('checkboxAttr')).toBe(true);
        });
    });
});

//# sourceMappingURL=listItemViewTests.js.map