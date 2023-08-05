'use strict';

$(function () {
    var $accessToken = $('#id_asana_access_token');
    var $workspace = $('#id_asana_workspace');
    var $error = $('<div class="errorlist">').insertAfter($accessToken).hide();

    $workspace.selectize({
        create: false,
        dropdownParent: 'body',
        searchField: 'name',
        valueField: 'id',
        labelField: 'name',
        render: {
            option: function option(item, escape) {
                return '<div>' + escape(item.name) + '</div>';
            }
        },
        onChange: function onChange(value) {
            $('#id_asana_workspace_name').val(this.options[value].name);
        }
    });

    var selectize = $workspace[0].selectize;
    selectize.$control.width($('#id_name').width());
    selectize.disable();

    function showError(errorStr) {
        $error.html('<span class="rb-icon rb-icon-warning"></span>\n' + _.escape(errorStr)).show();
    }

    var lastKey = null;

    var changeWorkspaceEnabled = _.throttle(function () {
        var apiKey = $accessToken.val().trim();

        if (lastKey === apiKey) {
            return;
        }

        lastKey = apiKey;
        $error.hide();
        selectize.disable();

        if (apiKey.length === 0) {
            return;
        }

        selectize.load(function (callback) {
            var params = $.param({ api_key: apiKey });

            $.ajax({
                url: SITE_ROOT + 'rbintegrations/asana/workspaces/?' + params,
                type: 'GET',
                success: function success(res) {
                    if (res.result === 'success') {
                        selectize.enable();
                        callback(res.data);
                    } else if (res.result === 'error') {
                        showError(res.error);
                        callback();
                    } else {
                        console.error('Unexpected error when fetching ' + 'Asana workspace list', res);
                        showError('Unable to communicate with Asana');
                        callback();
                    }
                },
                error: function error(xhr, textStatus, errorThrown) {
                    console.error('Unexpected error when fetching ' + 'Asana workspace list', xhr);
                    showError('Unable to communicate with Asana');
                    callback();
                }
            });
        });
    }, 100);

    $accessToken.on('change keyup', changeWorkspaceEnabled);
    changeWorkspaceEnabled();
});

//# sourceMappingURL=integrationConfig.js.map