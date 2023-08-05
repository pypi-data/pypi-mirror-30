'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

suite('djblets/forms/views/ListEditView', function () {
    var addImgUrl = '/static/admin/img/icon_addlink.gif';
    var delImgUrl = '/static/admin/img/icon_deletelink.gif';

    /*
     * See templates/djblets_forms/list_edit_widget.html.
     */
    var formTemplate = _.template('<div class="list-edit-widget" id="<%- id %>_container">\n <ul>\n <% if (items.length > 0) { %>\n  <% items.forEach(function(item, i) { %>\n   <li class="list-edit-entry" data-list-index="<%- i %>">\n    <input value="<%- item %>" type="text"<%- attrs %>>\n    <a href="#" class="list-edit-remove-item">\n     <img src="' + delImgUrl + '">\n    </a>\n   </li>\n  <% }); %>\n <% } else { %>\n   <li class="list-edit-entry" data-list-index="0">\n    <input type="text">\n    <a href="#" class="list-edit-remove-item">\n     <img src="' + delImgUrl + '">\n    </a>\n   </li>\n <% } %>\n  <li>\n   <a href="#" class="list-edit-add-item"><img src="' + addImgUrl + '"></a>\n  </li>\n </ul>\n <input id="<%- id %>" type="hidden"\n        value="<%- nonZeroItems.join(\',\') %>">\n</div>');

    var makeView = function makeView() {
        var items = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
        var attrs = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : '';

        attrs = attrs.length ? ' ' + attrs : '';

        $testsScratch.append($(formTemplate({
            items: items,
            nonZeroItems: items.filter(function (i) {
                return i.length > 0;
            }),
            attrs: attrs,
            id: 'list-edit'
        })));

        var view = new Djblets.Forms.ListEditView({
            el: '#list-edit_container',
            inputAttrs: attrs,
            deleteImageUrl: delImgUrl,
            sep: ','
        });

        view.render();

        return [view, view.$('#list-edit')];
    };

    describe('Updating fields', function () {
        it('With no values', function () {
            var _makeView = makeView([]),
                _makeView2 = _slicedToArray(_makeView, 2),
                $valueField = _makeView2[1];

            expect($valueField.val()).toEqual('');
        });

        it('With one value', function () {
            var _makeView3 = makeView(['One']),
                _makeView4 = _slicedToArray(_makeView3, 2),
                view = _makeView4[0],
                $valueField = _makeView4[1];

            expect($valueField.val()).toEqual('One');

            view.$('.list-edit-entry input').val('Foo').blur();
            expect($valueField.val()).toEqual('Foo');
        });

        it('With multiple values', function () {
            var _makeView5 = makeView(['one', 'two', 'three']),
                _makeView6 = _slicedToArray(_makeView5, 2),
                view = _makeView6[0],
                $valueField = _makeView6[1];

            var $inputs = view.$('.list-edit-entry input');

            expect($valueField.val()).toEqual('one,two,three');

            $inputs.eq(2).val('baz').blur();
            expect($valueField.val()).toEqual('one,two,baz');

            $inputs.eq(0).val('').blur();
            expect($valueField.val()).toEqual('two,baz');

            $inputs.eq(1).val('').blur();
            expect($valueField.val()).toEqual('baz');

            $inputs.eq(2).val('').blur();
            expect($valueField.val()).toEqual('');
        });
    });

    describe('Removal', function () {
        it('With no values', function () {
            var _makeView7 = makeView([]),
                _makeView8 = _slicedToArray(_makeView7, 2),
                view = _makeView8[0],
                $valueField = _makeView8[1];

            expect($valueField.val()).toEqual('');
            expect(view.$('.list-edit-entry').length).toEqual(1);

            view.$('.list-edit-remove-item').click();
            expect($valueField.val()).toEqual('');
            expect(view.$('.list-edit-entry').length).toEqual(1);
        });

        it('With one value', function () {
            var _makeView9 = makeView(['One']),
                _makeView10 = _slicedToArray(_makeView9, 2),
                view = _makeView10[0],
                $valueField = _makeView10[1];

            expect($valueField.val()).toEqual('One');

            view.$('.list-edit-remove-item').click();
            expect($valueField.val()).toEqual('');
            expect(view.$('.list-edit-entry').length).toEqual(1);
        });

        it('With multiple values', function () {
            var _makeView11 = makeView(['One', 'Two', 'Three']),
                _makeView12 = _slicedToArray(_makeView11, 2),
                view = _makeView12[0],
                $valueField = _makeView12[1];

            expect($valueField.val()).toEqual('One,Two,Three');

            view.$('.list-edit-remove-item').eq(1).click();
            expect($valueField.val()).toEqual('One,Three');
            expect(view.$('.list-edit-entry').length).toEqual(2);

            view.$('.list-edit-remove-item').eq(1).click();
            expect($valueField.val()).toEqual('One');
            expect(view.$('.list-edit-entry').length).toEqual(1);

            view.$('.list-edit-remove-item').click();
            expect($valueField.val()).toEqual('');
            expect(view.$('.list-edit-entry').length).toEqual(1);
        });
    });

    describe('Addition', function () {
        it('With values', function () {
            var _makeView13 = makeView(['one', 'two', 'three']),
                _makeView14 = _slicedToArray(_makeView13, 2),
                view = _makeView14[0],
                $valueField = _makeView14[1];

            expect($valueField.val()).toEqual('one,two,three');

            view.$('.list-edit-add-item').click();
            expect($valueField.val()).toEqual('one,two,three');
            expect(view.$('.list-edit-entry').length).toEqual(4);

            view.$('.list-edit-entry input').eq(3).val('four').blur();
            expect($valueField.val()).toEqual('one,two,three,four');
        });

        it('With blank values', function () {
            var _makeView15 = makeView(['', '', '']),
                _makeView16 = _slicedToArray(_makeView15, 2),
                view = _makeView16[0],
                $valueField = _makeView16[1];

            expect($valueField.val()).toEqual('');

            view.$('.list-edit-add-item').click();
            expect($valueField.val()).toEqual('');
            expect(view.$('.list-edit-entry').length).toEqual(4);

            view.$('.list-edit-entry input').eq(3).val('four').blur();
            expect($valueField.val()).toEqual('four');
        });

        it('With correct attributes', function () {
            var _makeView17 = makeView([], 'size="100" readonly'),
                _makeView18 = _slicedToArray(_makeView17, 1),
                view = _makeView18[0];

            view.$('.list-edit-add-item').click();
            var $input = view.$('input').eq(1);
            expect($input.attr('size')).toEqual('100');
            expect($input.prop('readonly')).toBe(true);
        });
    });
});

//# sourceMappingURL=listEditViewTests.js.map