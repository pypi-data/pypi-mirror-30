'use strict';

(function () {

    /**
     * An inline editor view for selecting Asana tasks.
     */
    var AsanaInlineEditorView = RB.InlineEditorView.extend({
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
                        return _.pick(selectize.options[key], ['completed', 'id', 'workspace_id', 'name']);
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
            return $('<select multiple class="asana-field">');
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
     * A review request field view for selecting Asana tasks.
     */
    RB.ReviewRequestFields.AsanaFieldView = RB.ReviewRequestFields.TextFieldView.extend({
        autocomplete: {},
        multiline: true,
        useEditIconOnly: true,

        taskTemplate: _.template('<<%- tagName %> class="asana-task<% if (completed) { %> completed<% } %>">\n <a href="https://app.asana.com/0/<%- workspaceId %>/<%- taskId %>/">\n  <div class="asana-task-checkbox">\n   <svg viewBox="0 0 32 32">\'\n    <polygon points="27.672,4.786 10.901,21.557 4.328,14.984 1.5,17.812 10.901,27.214 30.5,7.615"></polygon>\n   </svg>\n  </div>\n  <span><%- taskSummary %></span>\n </a>\n</<%- tagName %>>'),

        /**
         * Format the contents of the field.
         *
         * This will apply the contents of the model attribute to the field
         * element. If the field defines a ``formatValue`` method, this will use
         * that to do the formatting. Otherwise, the element will just be set to
         * contain the text of the value.
         */
        _formatField: function _formatField() {
            var fieldName = this.jsonFieldName || this.fieldID;
            var opts = { useExtraData: this.useExtraData };
            var tasks = JSON.parse(this.model.getDraftField(fieldName, opts));
            this._renderValue(tasks);
        },


        /**
         * Render the current value of the field.
         *
         * Args:
         *     tasks (Array of object):
         *         The current value of the field.
         */
        _renderValue: function _renderValue(tasks) {
            var _this2 = this;

            var lis = tasks.map(function (task) {
                return _this2.taskTemplate({
                    completed: task.completed,
                    workspaceId: task.workspace_id,
                    taskId: task.task_id,
                    taskSummary: task.name,
                    tagName: 'li'
                });
            });

            this.$el.html('<ul>' + lis.join('') + '</ul>');
        },


        /**
         * Return the type to use for the inline editor view.
         *
         * Returns:
         *     function:
         *     The constructor for the inline editor class to instantiate.
         */
        _getInlineEditorClass: function _getInlineEditorClass() {
            return AsanaInlineEditorView;
        },


        /**
         * Add auto-complete functionality to the field.
         */
        _buildAutoComplete: function _buildAutoComplete() {
            var _this3 = this;

            var reviewRequest = this.model.get('reviewRequest');
            var localSite = reviewRequest.get('localSitePrefix');
            var reviewRequestId = reviewRequest.get('id');
            var url = SITE_ROOT + 'rbintegrations/asana/' + localSite + 'task-search/' + reviewRequestId + '/';
            var $field = this.inlineEditorView.$field;
            var tasks = this.$el.data('raw-value');

            this._renderValue(tasks || []);

            $field.selectize({
                copyClassesToDropdown: true,
                dropdownParent: 'body',
                labelField: 'name',
                valueField: 'id',
                multiple: true,
                options: tasks,
                items: _.pluck(tasks, 'id'),
                optgroupLabelField: 'workspace',
                searchField: 'name',
                sortField: [{ 'field': 'completed' }, { 'field': 'name' }],
                render: {
                    option: function option(data, escape) {
                        return _this3.taskTemplate({
                            completed: data.completed,
                            workspaceId: data.workspace_id,
                            taskId: data.id,
                            taskSummary: data.name,
                            tagName: 'div'
                        });
                    }
                },
                load: function load(query, callback) {
                    var _this4 = this;

                    var params = $.param({ q: query });

                    $.ajax({
                        url: url + '?' + params,
                        type: 'GET',
                        error: callback.bind(this),
                        success: function success(res) {
                            var items = [];

                            _this4.clearOptionGroups();

                            for (var i = 0; i < res.length; i++) {
                                var group = res[i];
                                _this4.addOptionGroup(group.workspace, group);

                                for (var j = 0; j < group.tasks.length; j++) {
                                    var task = group.tasks[j];
                                    task.optgroup = group.workspace;
                                    task.workspace_id = group.workspace_id;

                                    var notesLines = task.notes.split('\n');
                                    task.notes = notesLines.splice(8).join('\n');

                                    items.push(task);
                                }
                            }

                            _this4.refreshOptions();
                            callback(items);
                        }
                    });
                }
            });
        }
    });
})();

//# sourceMappingURL=asanaFieldView.js.map