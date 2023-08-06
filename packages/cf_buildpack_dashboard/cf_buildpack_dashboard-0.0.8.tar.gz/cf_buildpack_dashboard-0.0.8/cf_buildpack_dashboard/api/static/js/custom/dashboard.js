var $ = require('jquery');
require('bootstrap');
var CollapsibleLists = require('./collapsible-list.js');

/**
* Creates a new card, as in https://getbootstrap.com/docs/4.0/components/card/
**/
function createNewCard(cardTitle, cardText){

    var $divNewCard = $('<div>', {class: 'card w-100'}),
        $divCardBody = $('<div>', {class: 'card-body'}),
        $divCardTitle = $('<h4>', {class: 'card-title'}).append(cardTitle),
        $divCardText = $('<p>', {class: 'card-text'}).append(cardText);

    var $divNewCardComplete = $divNewCard
                .append($divCardTitle, $divCardText)
                .append($divCardBody);

    return $divNewCardComplete;
}

export { createNewCard };
/**
* Parses and appends to $parent dictionary items representing app instances
**/
function appendAppsUl(apps, $parent){

        var $running_apps = $('<ul>'),
            $other_apps = $('<ul>'),
            $apps_ul = $('<ul>');

        var runningCount = 0,
            othersCount = 0;

        $.each(apps, function(appIndex, appEntry) {

            var $appEntryItem = $('<li>', {class: 'list-group-item list-group-item-warning'})
                .text(appEntry.name + (appEntry.autodetected ? " (A)" : ""));

            if (appEntry.running) {
                $appEntryItem.addClass('list-group-item-warning')
                $running_apps.append($appEntryItem);
                runningCount++;
            } else {
                $appEntryItem.addClass('list-group-item-danger')
                $other_apps.append($appEntryItem);
                othersCount++;
            }
        });

        $parent
            .append($running_apps)
            .append($other_apps);

        return { running: runningCount, total: (runningCount + othersCount) }
}

/**
* Parses and appends to $parent dictionary items
**/
function appendNestedUl(elements, $parent){

        var $ul = $('<ul>');

        var runningCount = 0,
            totalCount = 0;

        $.each(elements, function(elementKey, values){
            //each item has an entry and a badge
            var $liEntrySpan = $('<span>', {class: 'badge badge-default badge-pill'}),
                $liEntryItem = $('<li>', {class: 'list-group-item list-group-item-info'})
                    .text(elementKey)
                    .append($liEntrySpan)
                    .appendTo($ul);

            var appsCount = appendAppsUl(values, $liEntryItem);
            $liEntrySpan.text(appsCount.running + " running of " + appsCount.total + " total" );

            runningCount += appsCount.running;
            totalCount += appsCount.total;
        });

        $parent.append($ul);
        return { running: runningCount, total: totalCount }
}

/**
* Renders a collapsable list
**/
function renderCollapsableList(elements, ulId) {

        var $ul = $('<ul>', {class: 'collapsibleList list-group'});

        $.each( elements, function( elementKey, values ) {
            var $liEntrySpan = $('<span>', {class: 'badge badge-default badge-pill'}),
                $liEntryItem = $('<li>', {class: 'list-group-item list-group-item-success'})
                .text(elementKey)
                .append($liEntrySpan)
                .appendTo($ul);

            var elementsCount = appendNestedUl(values, $liEntryItem);
            $liEntrySpan.text(elementsCount.running + " running of " + elementsCount.total + " total");

        });

        return $ul;
}

var renderList = function(jsonData, divId, cardId) {
    return new Promise(function(resolve, reject) {
                var $topLevel_ul = renderCollapsableList(jsonData, divId);
                resolve($topLevel_ul);
            })
            .then(function($topLevel_ul){
                $("#" + cardId + " div.card-body").append($topLevel_ul);
                return 'success';
            })
            .then(function(){
                CollapsibleLists.applyTo(document.getElementById(divId, true));
            })
            .catch(error => { console.log('error while rendering list', error.message); })
}

export { renderList };

var fetchData = function(query, dataURL) {
    // Return the $.ajax promise
    return $.get({
        data: query,
        dataType: 'json',
        url: dataURL
    });
}

function getAllData() {

    var getBuildpacks = fetchData(
        {
            "by_buildpack": "true",
            "environment": getEnvironment()
        }, "/api/buildpacks"),
        getOrganisations = fetchData(
        {
            "by_buildpack": "false",
            "environment": getEnvironment()
        }, "/api/buildpacks");

    getOrganisations.done(function(jsonData){
            renderList(jsonData, "organisations_div", "organisations_card");
    })

    getOrganisations.fail(function(jsonData){
        alert( "Request failed: " + 'Error requesting buildpack data' );
    })

    getBuildpacks.done(function(jsonData){
            renderList(jsonData, "buildpacks_div", "buildpacks_card");
    })

    getBuildpacks.fail(function(jsonData){
        alert( "Request failed: " + 'Error requesting buildpack data' );
    })
}

function getEnvironment() {
    var env = $('input[name=environments]:checked').val();
    return env
}

$( document ).ready(function() {

    var $buildpacksCard = createNewCard("Buildpacks", "Apps grouped by buildpack and organisation");
    $buildpacksCard.attr("id", "buildpacks_card");
    $("#buildpacks_div").append($buildpacksCard);

    var $organisationsCard = createNewCard("Organisations", "Apps grouped by organisation and buildpack");
    $organisationsCard.attr("id", "organisations_card");
    $("#organisations_div").append($organisationsCard);

    $('input[type=radio][name=environments]').change(function() {
        if (!this.checked) {
            this.click();
        }
        $("#buildpacks_div .collapsibleList").remove();
        $("#organisations_div .collapsibleList").remove();
        getAllData();
    });

    getAllData();
});
