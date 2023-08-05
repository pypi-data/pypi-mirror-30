'use strict';

(function () {

    /**
     * An inline editor view for selecting Trello cards.
     */
    var TrelloInlineEditorView = RB.InlineEditorView.extend({
        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         Options for the view.
         */
        initialize: function initialize(options) {
            var _this = this;

            options = _.defaults(options, {
                hasRawValue: true,
                formatResult: function formatResult(value) {
                    if (value && value.name) {
                        return value.name.htmlEncode();
                    } else {
                        return '';
                    }
                },
                getFieldValue: function getFieldValue(editor) {
                    var selectize = _this.$field[0].selectize;
                    var selected = selectize.getValue();

                    return JSON.stringify(selected.map(function (key) {
                        return selectize.options[key];
                    }));
                },
                isFieldDirty: function isFieldDirty(editor, initialValue) {
                    var value = editor.getValue();
                    return initialValue !== value;
                },
                setFieldValue: function setFieldValue(editor, value) {
                    // This is a no-op, since we do this in the $.selectize call.
                }
            });

            RB.InlineEditorView.prototype.initialize.call(this, options);
        },


        /**
         * Create and return the field to use for the input element.
         *
         * Returns:
         *     jQuery:
         *     The newly created input element.
         */
        createField: function createField() {
            return $('<select multiple class="trello-field">');
        },


        /**
         * Connect events.
         */
        setupEvents: function setupEvents() {
            RB.InlineEditorView.prototype.setupEvents.call(this);

            this.$field.on('change', this._scheduleUpdateDirtyState.bind(this));
        },


        /**
         * Show the editor.
         *
         * Args:
         *     options (object, optional):
         *         Options for showing the editor.
         */
        showEditor: function showEditor() {
            var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

            RB.InlineEditorView.prototype.showEditor.call(this, options);

            if (this.options.focusOnOpen) {
                this.$field[0].selectize.focus();
            }
        }
    });

    /**
     * A review request field view for selecting Trello cards.
     */
    RB.ReviewRequestFields.TrelloFieldView = RB.ReviewRequestFields.TextFieldView.extend({
        autocomplete: {},
        multiline: true,
        useEditIconOnly: true,

        cardTemplate: _.template('<<%- tagName %> class="trello-card">\n <div class="trello-card-card">\n  <a href="<%- url %>"><%- name %></a>\n </div>\n <div class="trello-card-details">\n  on <span class="trello-card-list"><%- list %></span>\n  in <span class="trello-card-board"><%- board %></span>\n </div>\n</<%- tagName %>>'),

        /**
         * Format the contents of the field.
         *
         * This will apply the contents of the model attribute to the field
         * element. If the field defines a ``formatValue`` method, this will use
         * that to do the formatting. Otherwise, the element will just be set to
         * contain the text of the value.
         */
        _formatField: function _formatField() {
            var cards = JSON.parse(this.model.getDraftField(this.jsonFieldName || this.fieldID, {
                useExtraData: this.useExtraData
            }));
            this._renderValue(cards);
        },


        /**
         * Render the current value of the field.
         *
         * Args:
         *     cards (Array of object):
         *         The current set of cards to list.
         */
        _renderValue: function _renderValue(cards) {
            var _this2 = this;

            var items = cards.map(function (card) {
                return _this2.cardTemplate(_.defaults({
                    tagName: 'li'
                }, card));
            });
            this.$el.html('<ul>' + items.join('') + '</ul>');
        },


        /**
         * Return the type to use for the inline editor view.
         *
         * Returns:
         *     function:
         *     The constructor for the inline editor class to instantiate.
         */
        _getInlineEditorClass: function _getInlineEditorClass() {
            return TrelloInlineEditorView;
        },


        /**
         * Add auto-complete functionality to the field.
         */
        _buildAutoComplete: function _buildAutoComplete() {
            var _this3 = this;

            var reviewRequest = this.model.get('reviewRequest');
            var localSite = reviewRequest.get('localSitePrefix');
            var reviewRequestId = reviewRequest.get('id');
            var url = SITE_ROOT + 'rbintegrations/trello/' + localSite + 'card-search/' + reviewRequestId + '/';
            var $field = this.inlineEditorView.$field;
            var cards = this.$el.data('raw-value');

            this._renderValue(cards || []);

            $field.selectize({
                copyClassesToDropdown: true,
                dropdownParent: 'body',
                multiple: true,
                labelField: 'name',
                valueField: 'id',
                searchField: 'name',
                options: cards,
                items: _.pluck(cards, 'id'),
                render: {
                    option: function option(data, escape) {
                        return _this3.cardTemplate(_.defaults({
                            tagName: 'div'
                        }, data));
                    }
                },
                load: function load(query, callback) {
                    var params = $.param({ q: query });

                    $.ajax({
                        url: url + '?' + params,
                        type: 'GET',
                        error: callback.bind(this),
                        success: function success(res) {
                            return callback(res);
                        }
                    });
                }
            });
        }
    });
})();

//# sourceMappingURL=trelloFieldView.js.map