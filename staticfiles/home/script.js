// Register the plugins
gsap.registerPlugin(CSSPlugin, TextPlugin);

/* --- Load elements from the HTML DOM --- */

const body = document.getElementsByTagName("body");

// Rows
const upperRow = document.getElementById("upper-row");
const lowerRow = document.getElementById("lower-row");

// Panels
const ulPanel = document.getElementById("ul-panel");
const urPanel = document.getElementById("ur-panel");
const blPanel = document.getElementById("bl-panel");
const brPanel = document.getElementById("br-panel");

// Panel Interiors
const ulInterior = document.getElementById("ul-interior")
const urInterior = document.getElementById("ur-interior")
const blInterior = document.getElementById("bl-interior")
const brInterior = document.getElementById("br-interior")

// Panel Buttons
const ulBttn = ulInterior.getElementsByTagName('button')[0];
const urBttn = urInterior.getElementsByTagName('button')[0];
const blBttn = blInterior.getElementsByTagName('button')[0];
const brBttn = brInterior.getElementsByTagName('button')[0];

/* --- Utility for organizing elements for each quadrant --- */

class Quad {
    constructor() {
        this.grid = [[-1,-1],[-1,-1]];
    }

    insert(r, c, item) {
        this.grid[r][c] = item;
    }

    getItem(r, c) {
        return this.grid[r][c];
    }
}

/* --- Create the arrays for automating access to the HTML page ---- */

const rows = Array();
rows.push(upperRow);
rows.push(lowerRow);

const panels = new Quad();
panels.insert(0,0, ulPanel);
panels.insert(0,1, urPanel);
panels.insert(1,0, blPanel);
panels.insert(1,1, brPanel);

const interiors = new Quad();
interiors.insert(0,0, ulInterior);
interiors.insert(0,1, urInterior);
interiors.insert(1,0, blInterior);
interiors.insert(1,1, brInterior);

const buttons = new Quad();
buttons.insert(0,0, ulBttn);
buttons.insert(0,1, urBttn);
buttons.insert(1,0, blBttn);
buttons.insert(1,1, brBttn);

/* --- Colors --- */

beige = '#F2D8D8';
green = '#5C8984';
lightGray = '#545B77';
darkGray = '#374259';

/* --- Layouts for each panel --- */

const borderRadii = new Quad();
borderRadii.insert(0,0, '0 0 30% 0');
borderRadii.insert(0,1, '0 0 0 30%');
borderRadii.insert(1,0, '0 30% 0 0');
borderRadii.insert(1,1, '30% 0 0 0');

const paddings = new Quad();
paddings.insert(0,0, '0 40px 40px 0');
paddings.insert(0,1, '0 0 40px 40px');
paddings.insert(1,0, '40px 40px 0 0');
paddings.insert(1,1, '40px 0 0 40px');

/* --- CSS Styles based on status --- */

defaultRow = {'height': '50%'};
expandedRow = {'height': '80%'};
shrunkenRow = {'height': '20%'};

expandedPanel = {
    'width': '75%',
    'background-color': darkGray,
    'color': 'white',
};
shrunkenPanel = {
    'width': '25%',
    'background-color': lightGray,
    'color': 'black',
    'border-radius': '0% 0% 0% 0%',
};
defaultPanel = {
    'width': '50%',
    'background-color': lightGray,
    'color': 'black',
    'border-radius': '0% 0% 0% 0%',
}

expandedInterior = { 'background-color': green };
defaultInterior = { 'background-color': lightGray }


expandedText = { 'font-size': '200px',
                'background-color': green,
                'color': 'white' };
defaultText = { 'font-size': '75px',
                 'background-color': lightGray,
                 'color': 'black'  };

/* --- Animation Code --- */

function adjustRows(tm, r) {
    tm.to(rows[r], expandedRow, 0);
    tm.to(rows[+ !r], shrunkenRow, 0);
}

let bodySet = false;

function adjustPanels(tm, r, c) {
    if(!bodySet) {
        tm.to(body, {'background-color':lightGray}, 0);
        bodySet = true;
    }

    tm.to(panels.getItem(r,c), expandedPanel, 0);
    tm.to(panels.getItem(r,+ !c), shrunkenPanel, 0);
    tm.to(panels.getItem(+ !r, 0), defaultPanel, 0);
    tm.to(panels.getItem(+ !r, 1), defaultPanel, 0);

    tm.to(panels.getItem(r, c), {'border-radius':borderRadii.getItem(r,c)}, 0);
    tm.to(panels.getItem(r, c), {'padding': paddings.getItem(r,c)}, 0);
}

function adjustInteriors(tm, r, c) {
    tm.to(interiors.getItem(r, c), expandedInterior, 0);
    tm.to(interiors.getItem(r,+ !c), defaultInterior, 0);
    tm.to(interiors.getItem(+ !r, 0), defaultInterior, 0);
    tm.to(interiors.getItem(+ !r, 1), defaultInterior, 0);

    tm.to(interiors.getItem(r, c), {'border-radius': borderRadii.getItem(r,c)}, 0);
}

function adjustText(tm, r, c) {
    tm.to(buttons.getItem(r, c), expandedText, 0);
    tm.to(buttons.getItem(r,+ !c), defaultText, 0);
    tm.to(buttons.getItem(+ !r, 0), defaultText, 0);
    tm.to(buttons.getItem(+ !r, 1), defaultText, 0);
}

function entering(r, c) {
    const tm = gsap.timeline();

    adjustRows(tm, r);
    adjustPanels(tm, r, c);
    adjustInteriors(tm, r, c);
    adjustText(tm, r,c);

    tm.play();
}

/* --- Event listeners --- */

ulPanel.addEventListener('mouseenter', () => entering(0,0));
urPanel.addEventListener('mouseenter', () => entering(0,1));
blPanel.addEventListener('mouseenter', () => entering(1,0));
brPanel.addEventListener('mouseenter', () => entering(1,1));

/* --- Redirects --- */

ulBttn.onclick = function () { location.href = 'solar'; };
urBttn.onclick = function () { location.href = 'wind'; };
blBttn.onclick = function () { location.href = 'insights'; };
brBttn.onclick = function () { location.href = 'contact'; };
