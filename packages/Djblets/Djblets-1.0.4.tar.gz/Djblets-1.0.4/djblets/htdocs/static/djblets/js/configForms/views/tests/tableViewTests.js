'use strict';

suite('djblets/configForms/views/TableView', function () {
    describe('Manages rows', function () {
        var collection = void 0;
        var list = void 0;
        var tableView = void 0;

        beforeEach(function () {
            collection = new Backbone.Collection([{ text: 'Item 1' }, { text: 'Item 2' }, { text: 'Item 3' }], {
                model: Djblets.Config.ListItem
            });

            list = new Djblets.Config.List({}, {
                collection: collection
            });

            tableView = new Djblets.Config.TableView({
                model: list
            });
            tableView.render();
        });

        it('On render', function () {
            var $rows = tableView.$('tr');
            expect($rows.length).toBe(3);
            expect($rows.eq(0).text().strip()).toBe('Item 1');
            expect($rows.eq(1).text().strip()).toBe('Item 2');
            expect($rows.eq(2).text().strip()).toBe('Item 3');
        });

        it('On add', function () {
            collection.add({
                text: 'Item 4'
            });

            var $rows = tableView.$('tr');
            expect($rows.length).toBe(4);
            expect($rows.eq(3).text().strip()).toBe('Item 4');
        });

        it('On remove', function () {
            collection.remove(collection.at(0));

            var $rows = tableView.$('tr');
            expect($rows.length).toBe(2);
            expect($rows.eq(0).text().strip()).toBe('Item 2');
        });

        it('On reset', function () {
            collection.reset([{ text: 'Foo' }, { text: 'Bar' }]);

            var $rows = tableView.$('tr');
            expect($rows.length).toBe(2);
            expect($rows.eq(0).text().strip()).toBe('Foo');
            expect($rows.eq(1).text().strip()).toBe('Bar');
        });
    });
});

//# sourceMappingURL=tableViewTests.js.map