// Objects from the HTML DOM
const dsInfoPanel = document.getElementById("datasets-info-panel");
const mdInfoPanel = document.getElementById("models-info-panel");
const backButton = document.getElementById('back-button').querySelector('button');

// ID's for the different panels
const dsIntId = '#datasets-intro-panel';
const dsSelId = '#datasets-select-panel';
const dsInfId = '#datasets-info-panel';

const mdIntId = '#models-intro-panel';
const mdSelId = '#models-select-panel';
const mdInfId = '#models-info-panel';

const backButtonId = '#back-button';

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
    timeline.to(backButtonId, {x:'100%', opacity:'0'}, t_hide);
    timeline.to(backButtonId, {x:'0', opacity: '100%'}, t_show);
}

/* --- Intro Handling --- */

function introClicked(side) {
    let tm = gsap.timeline();

    dimInfoPanelHeader(side);
    toggleBackButton(tm, 0, 2);

    // Hide main panels
    tm.to(dsIntId, {x:'-=100%'}, 0);
    tm.to(mdIntId, {x:'+=110%'}, 0);
    tm.set('.intro-panel', {display:'none'}, 1);

    let selPanel = (side === 'models' ? mdSelId : dsSelId);
    let infPanel = (side === 'models' ? mdInfId : dsInfId);

    // Make panels visible
    tm.set(selPanel, {display:'block'}, 1);
    tm.set(infPanel, {display:'block'}, 1);

    // Move into display from a vertical direction
    tm.from(selPanel, {y:'-100%'}, 1);
    tm.from(infPanel, {y:'100%'}, 1);

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

function datasetItemSelected(item) {
    const dataset = data.datasets.find(obj => obj.name === item);

    const header = dsInfoPanel.querySelector('.info-header > p');
    const content = dsInfoPanel.querySelector('.info-content > p');
    const contBttn = dsInfoPanel.querySelector('.info-button > button');

    // Update the info display with information about selected dataset
    header.textContent = dataset.name;
    content.textContent = dataset.description;

    contBttn.onclick = function () { location.href = dataset.link; }
}

function modelItemSelected(item) {
    const dataset = data.models.find(obj => obj.name === item);

    const header = mdInfoPanel.querySelector('.info-header > p');
    const content = mdInfoPanel.querySelector('.info-content > p');
    const contBttn = mdInfoPanel.querySelector('.info-button > button');

    // Update the info display with information about selected model
    header.textContent = dataset.name;
    content.textContent = dataset.description;

    contBttn.onclick = function () { location.href = dataset.link; }
}

/* --- Back button Click ---*/

backButton.onclick = function () { location.href = '/'; };