'use strict';

var $ = require('jquery');

const dashboard = require("../dashboard.js");

const organisations = {
    "CATS-persistent-org": {
        "https://github.com/cloudfoundry/java-buildpack.git#v4.0": [
            {
                "name": "cache-by-default",
                "running": false,
                "autodetected": false
                }
        ]
    }
}

test('test list rendering', async () => {
  expect.assertions(6);

      // Set up our document body
  document.body.innerHTML =
    '<div id=organisations_div>' +
    '</div>';

    var $organisationsCard = await dashboard.createNewCard("Organisations", "Apps grouped by organisation and buildpack");
    $organisationsCard.attr("id", "organisations_card");
    $("#organisations_div").append($organisationsCard);
    await dashboard.renderList(organisations, "organisations_div", "organisations_card");

    expect($('#organisations_card > .card-title').text()).toEqual("Organisations");
    expect($('#organisations_card > .card-text').text()).toEqual("Apps grouped by organisation and buildpack");

    var $organisationsCard = $('.card-body > ul > li');
    expect($organisationsCard.attr('class')).toContain("collapsibleListClosed");
    expect($organisationsCard.length).toEqual(1);

    var $buildpacksList = $('.card-body > ul > li > ul > li');
    expect($buildpacksList.attr('class')).toContain("collapsibleListClosed");
    expect($buildpacksList.length).toEqual(1);
});
