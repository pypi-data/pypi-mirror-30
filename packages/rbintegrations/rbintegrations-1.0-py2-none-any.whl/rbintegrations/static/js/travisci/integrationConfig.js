'use strict';

$(function () {
    var $endpoint = $('#id_travis_endpoint');
    var $server = $('#row-travis_custom_endpoint');

    function changeServerVisibility() {
        $server.setVisible($endpoint.val() === 'E');
    }

    $endpoint.change(changeServerVisibility);
    changeServerVisibility();
});

//# sourceMappingURL=integrationConfig.js.map