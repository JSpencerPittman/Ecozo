/* --- Monitor Screen size -- */

function active() {
    var width = window.innerWidth
    || document.documentElement.clientWidth
    || document.body.clientWidth;
    return width >= 1300;
}

let desktop = active();

window.addEventListener("resize", function(event) {
    const isActive = active();
    if(isActive !== desktop) {
        desktop = isActive;
        location.reload();
    }
});

// Objects from the HTML DOM
const dsInfoPanel = document.getElementById("datasets-info-panel");
const mdInfoPanel = document.getElementById("models-info-panel");
const backButtonFull = document.getElementById('back-button-full').querySelector('button');
const backButtonHalf = document.getElementById('back-button-half').querySelector('button');
const utilityButton = document.getElementById('util-button').querySelector('button');


// ID's for the different panels
const dsIntId = '#datasets-intro-panel';
const dsSelId = '#datasets-select-panel';
const dsInfId = '#datasets-info-panel';

const mdIntId = '#models-intro-panel';
const mdSelId = '#models-select-panel';
const mdInfId = '#models-info-panel';

const buttonContId = '#button-container';
const backButtonFullId = '#back-button-full';
const backButtonHalfId = '#back-button-half';
const utilButtonId = '#util-button';

// JSON data with links and descriptions
let data;
fetch('../static/insights/data.json')
    .then((response) => response.json())
    .then((json) => data = json);

// Colors
const inactiveColor = '#395754';

/* --- Animation Code --- */

// Hides the button temporarily while the animations are taking place
function toggleBackButton(timeline, t_hide, t_show) {
    timeline.to(buttonContId, {x:'100%', opacity:'0'}, t_hide);
    timeline.to(buttonContId, {x:'0', opacity: '100%'}, t_show);
}

/* --- Intro Handling --- */

function introClicked(side) {
    if(active()) introClickedDesktop(side);
    else introClickedMobile(side);
}

function introClickedDesktop(side) {
    let tm = gsap.timeline();

    dimInfoPanelHeader(side);
    toggleBackButton(tm, 0, 2);

    // Hide main panels
    tm.to(dsIntId, {x:'-=100%'}, 0);
    tm.to(mdIntId, {x:'+=110%'}, 0);
    tm.set('.intro-panel', {display:'none'}, 1);

    // Make panels visible
    let selPanel = (side === 'models' ? mdSelId : dsSelId);
    let infPanel = (side === 'models' ? mdInfId : dsInfId);

    tm.set(selPanel, {display:'block'}, 1);
    tm.set(infPanel, {display:'block'}, 1);

    // Move into display from a vertical direction
    tm.from(selPanel, {y:'-100%'}, 1);
    tm.from(infPanel, {y:'100%'}, 1);

    tm.play()
}

function introClickedMobile(side) {
    let tm = gsap.timeline();

    toggleBackButton(tm, 0, 2);

    // Hide main panels
    tm.to(dsIntId, {x:'-=100%'}, 0);
    tm.to(mdIntId, {x:'+=120%'}, 0);
    tm.set('.intro-panel', {display:'none'}, 1);

    // make selection panel visible
    let selPanel = (side === 'models' ? mdSelId : dsSelId);

    tm.set(selPanel, {display:'block'}, 1);

    // Add toggle button to button container
    tm.set(backButtonFullId, {display:'none'}, 1);
    tm.set(backButtonHalfId, {display:'flex'}, 1);
    tm.set(utilButtonId, {display:'flex'}, 1);

    // Configure button
    utilityButton.textContent = (side === 'datasets' ? 'Models' : 'Datasets');
    utilityButton.onclick = function () {toggleSelectionPanels(side);};

    // Move into display from a vertical direction
    tm.from(selPanel, {y:'-100%'}, 1);

    tm.play()
}

/* --- Panel Switching --- */
// Set the panel header above the info panel to a dimmer shade to
//  indicate it isn't selected
function dimInfoPanelHeader(side) {
    const infoPanel = (side === 'models' ? mdInfoPanel : dsInfoPanel);
    const infoHeader = infoPanel.querySelector('.panel-header');
    const infoHeaderButton = infoHeader.querySelector('button');

    infoHeader.style.backgroundColor = inactiveColor;
    infoHeaderButton.style.backgroundColor = inactiveColor;
}

// Animation routine:
// 1) Move the panels into middle overlapping
// 2) Move both panels out of frame
// 3) Set their display to none
function hidePanels(tm, side) {
    let selPanel;
    let infPanel;
    let selX;
    let infX;

    if(side === 'models') {
        selPanel = dsSelId;
        infPanel = dsInfId;
        selX = '+=50%';
        infX = '-=50%';
    } else {
        selPanel = mdSelId;
        infPanel = mdInfId;
        selX = '-=50%';
        infX = '+=50%';
    }

    // Move in to the middle
    tm.to(selPanel, {x:selX}, 0);
    tm.to(infPanel, {x:infX}, 0);

    // Move downwards
    tm.to(selPanel, {y:'+=100%'}, 0.5);
    tm.to(infPanel, {y:'+=100%'}, 0.5);

    // Move back to original positions and hide
    tm.set(selPanel, {x: infX}, 1);
    tm.set(infPanel, {x: selX}, 1);

    tm.set(selPanel, {y: '-=100%'}, 1);
    tm.set(infPanel, {y: '-=100%'}, 1);

    tm.set(selPanel, {display: 'none'}, 1);
    tm.set(infPanel, {display: 'none'}, 1);
}

// Animation Routine:
// 1) Follows after hide_panels
// 2) Make the panels displayed as blocks
// 3) Move them to the opposite horizontal side offscreen
// 4) Slide them into normal position
function showPanels(tm, side) {
    let selPanel;
    let infPanel;
    let selX;
    let infX;

    if(side === 'models') {
        selPanel = mdSelId;
        infPanel = mdInfId;
        selX = '-=200%';
        infX = '+=200%';
    } else {
        selPanel = dsSelId;
        infPanel = dsInfId;
        selX = '+=200%';
        infX = '-=200%';
    }

    // Set display to block
    tm.set(selPanel, {display:'block'}, 1.5);
    tm.set(infPanel, {display:'block'}, 1.5);

    // Start them off on the opposite side
    tm.from(selPanel, {x:selX}, 1.5);
    tm.from(infPanel, {x:infX}, 1.5);
}

 function panelHeaderClicked(side) {
    const tm = gsap.timeline()
    toggleBackButton(tm, 0, 2);

    hidePanels(tm, side);
    showPanels(tm, side);
    dimInfoPanelHeader(side);
    tm.play();
 }

 /* --- Menu Selections --- */
function itemSelectedDesktop(item, side) {
    let dataset;
    let header;
    let content;
    let contBttn;

    if(side === 'datasets') {
        dataset = data.datasets.find(obj => obj.name === item);
        header = dsInfoPanel.querySelector('.info-header > p');
        content = dsInfoPanel.querySelector('.info-content > p');
        contBttn = dsInfoPanel.querySelector('.info-button > button');
    } else {
        dataset = data.models.find(obj => obj.name === item);
        header = mdInfoPanel.querySelector('.info-header > p');
        content = mdInfoPanel.querySelector('.info-content > p');
        contBttn = mdInfoPanel.querySelector('.info-button > button');
    }

     // Update the info display with information about selected item
    header.textContent = dataset.name;
    content.textContent = dataset.description;

    contBttn.onclick = function () { location.href = dataset.link; }
}

function itemSelectedMobile(item, side) {
    tm = gsap.timeline();

    toggleBackButton(tm, 0, 1.5);

    // Configure utility button
    utilityButton.textContent = (side === 'datasets' ? 'Datasets' : 'Models');
    utilityButton.onclick = function () {goBackToSelection(side);};

    // Hide the selection panel
    const selId = (side === 'datasets' ? dsSelId : mdSelId);
    tm.to(selId, {x:'+=120%'}, 0);
    tm.set(selId, {display:'none'}, 0.5);
    tm.set(selId, {x:'-=120%'}, 0.5);

    // Bring the info panel into view
    const infId = (side === 'datasets' ? dsInfId : mdInfId);
    tm.set(infId, {display:'flex'}, 0.5);
    tm.from(infId, {x:'-=100%'}, 1);

    tm.play();

    itemSelectedDesktop(item, side);
}

function itemSelected(item, side) {
    if(active()) itemSelectedDesktop(item, side);
    else itemSelectedMobile(item, side);
}

/* --- mobile specific animations --- */

function toggleSelectionPanels(side) {
    const tm = gsap.timeline();

    toggleBackButton(tm, 0, 1.5);

    // Configure button
    const utilText = (side === 'datasets' ? 'Datasets' : 'Models');
    const target = (side === 'datasets' ? 'models' : 'datasets');
    utilityButton.textContent = utilText;
    utilityButton.onclick = function () {toggleSelectionPanels(target);};

    // Hide the original panel
    const hideSelId = (side === 'datasets' ? dsSelId : mdSelId);
    tm.to(hideSelId, {y:'-=100%'}, 0);
    tm.set(hideSelId, {display:'none'}, 0.5);
    tm.set(hideSelId, {y:'+=100%'}, 1);

    // Display the other selection panel
    const showSelId = (side === 'datasets' ? mdSelId : dsSelId);
    tm.set(showSelId, {display:'block'}, 0.5);
    tm.from(showSelId, {y:'+=100%'}, 1);

    tm.play()
}

function goBackToSelection(side) {
    const tm = gsap.timeline();
    toggleBackButton(tm, 0, 1.5);

     // Configure button
    const utilText = (side === 'datasets' ? 'Models' : 'Datasets');
    const target = (side === 'datasets' ? 'datasets' : 'models');
    utilityButton.textContent = utilText;
    utilityButton.onclick = function () {toggleSelectionPanels(target);};

    // Hide the info panel
    const infId = (side === 'datasets' ? dsInfId : mdInfId);
    tm.to(infId, {x:'-=120%'}, 0);
    tm.set(infId, {display:'none'}, 0.5);
    tm.set(infId, {x:'+=120%'}, 1);

    // Display the selection panel
    let selId = (side === 'datasets' ? dsSelId : mdSelId);
    tm.set(selId, {display:'block'}, 0.5);
    tm.from(selId, {x:'+=120%'}, 1);

    tm.play()
}

/* --- Back button Click ---*/

backButtonFull.onclick = function () { location.href = '/'; };
backButtonHalf.onclick = function () { location.href = '/'; };