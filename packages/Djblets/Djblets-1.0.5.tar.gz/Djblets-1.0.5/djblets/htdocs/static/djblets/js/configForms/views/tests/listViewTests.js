'use strict';

suite('djblets/configForms/views/ListView', function () {
    describe('Manages items', function () {
        var collection = void 0;
        var list = void 0;
        var listView = void 0;

        beforeEach(function () {
            collection = new Backbone.Collection([{ text: 'Item 1' }, { text: 'Item 2' }, { text: 'Item 3' }], {
                model: Djblets.Config.ListItem
            });

            list = new Djblets.Config.List({}, {
                collection: collection
            });

            listView = new Djblets.Config.ListView({
                model: list
            });
            listView.render();
        });

        it('On render', function () {
            var $items = listView.$('li');
            expect($items.length).toBe(3);
            expect($items.eq(0).text().strip()).toBe('Item 1');
            expect($items.eq(1).text().strip()).toBe('Item 2');
            expect($items.eq(2).text().strip()).toBe('Item 3');
        });

        it('On add', function () {
            collection.add({
                text: 'Item 4'
            });

            var $items = listView.$('li');
            expect($items.length).toBe(4);
            expect($items.eq(3).text().strip()).toBe('Item 4');
        });

        it('On remove', function () {
            collection.remove(collection.at(0));

            var $items = listView.$('li');
            expect($items.length).toBe(2);
            expect($items.eq(0).text().strip()).toBe('Item 2');
        });

        it('On reset', function () {
            collection.reset([{ text: 'Foo' }, { text: 'Bar' }]);

            var $items = listView.$('li');
            expect($items.length).toBe(2);
            expect($items.eq(0).text().strip()).toBe('Foo');
            expect($items.eq(1).text().strip()).toBe('Bar');
        });
    });
});

//# sourceMappingURL=listViewTests.js.map