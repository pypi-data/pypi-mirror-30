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

            $appEntryItem = $('<li>', {class: 'list-group-item list-group-item-warning'}).text(appEntry.name);

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
            var $liEntrySpan = $('<span>', {class: 'badge badge-default badge-pill'})
                $liEntryItem = $('<li>', {class: 'list-group-item list-group-item-info'})
                    .text(elementKey)
                    .append($liEntrySpan)
                    .appendTo($ul);

            appsCount = appendAppsUl(values, $liEntryItem);
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

        var $ul = $('<ul>', {id: ulId, class: 'collapsibleList list-group'});

        $.each( elements, function( elementKey, values ) {
            var $liEntrySpan = $('<span>', {class: 'badge badge-default badge-pill'});
                $liEntryItem = $('<li>', {class: 'list-group-item list-group-item-success'})
                .text(elementKey)
                .append($liEntrySpan)
                .appendTo($ul);

            elementsCount = appendNestedUl(values, $liEntryItem);
            $liEntrySpan.text(elementsCount.running + " running of " + elementsCount.total + " total");

        });

        return $ul;
}

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

            $topLevel_ul = renderCollapsableList(jsonData, "organisations_div");
            $("#organisations_card div.card-body").append($topLevel_ul);
            CollapsibleLists.applyTo(document.getElementById("organisations_div", true));
    })

    getOrganisations.fail(function(jsonData){
        alert( "Request failed: " + 'Error requesting buildpack data' );
    })

    getBuildpacks.done(function(jsonData){

            $topLevel_ul = renderCollapsableList(jsonData, "buildpacks_div");
            $("#buildpacks_card div.card-body").append($topLevel_ul);
            CollapsibleLists.applyTo(document.getElementById("buildpacks_div", true));
    })

    getBuildpacks.fail(function(jsonData){
        alert( "Request failed: " + 'Error requesting buildpack data' );
    })
}

function getEnvironment() {
    env = $('input[name=environments]:checked').val();
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
