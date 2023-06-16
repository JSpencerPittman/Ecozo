// Register the plugins
gsap.registerPlugin(CSSPlugin, TextPlugin);

const body = document.getElementsByTagName("body");

const up_row = document.getElementById("upper-row");
const dw_row = document.getElementById("lower-row");

const ul_panel = document.getElementById("ul-panel");
const ur_panel = document.getElementById("ur-panel");
const bl_panel = document.getElementById("bl-panel");
const br_panel = document.getElementById("br-panel");

const ul_interior = document.getElementById("ul-interior")
const ur_interior = document.getElementById("ur-interior")
const bl_interior = document.getElementById("bl-interior")
const br_interior = document.getElementById("br-interior")

const ul_bttn = ul_interior.getElementsByTagName('button')[0];
const ur_bttn = ur_interior.getElementsByTagName('button')[0];
const bl_bttn = bl_interior.getElementsByTagName('button')[0];
const br_bttn = br_interior.getElementsByTagName('button')[0];

ul_panel.addEventListener('mouseenter', () => entering(0,0));
ur_panel.addEventListener('mouseenter', () => entering(0,1));
bl_panel.addEventListener('mouseenter', () => entering(1,0));
br_panel.addEventListener('mouseenter', () => entering(1,1));

rows = Array();
rows.push(up_row);
rows.push(dw_row);

panels = Array();
panels.push(Array());
panels.push(Array());
panels[0].push(ul_panel);
panels[0].push(ur_panel);
panels[1].push(bl_panel);
panels[1].push(br_panel);

interiors = Array();
interiors.push(Array());
interiors.push(Array());
interiors[0].push(ul_interior);
interiors[0].push(ur_interior);
interiors[1].push(bl_interior);
interiors[1].push(br_interior);

buttons = Array();
buttons.push(Array());
buttons.push(Array());
buttons[0].push(ul_bttn);
buttons[0].push(ur_bttn);
buttons[1].push(bl_bttn);
buttons[1].push(br_bttn);

color1 = '#545B77';
color2 = '#F2D8D8';
color3 = '#5C8984';
color4 = '#374259';

default_row = {'height': '50%'};

expand_row = {'height': '80%'};

shrink_row = {'height': '20%'};

border_radii = Array();
border_radii.push(Array());
border_radii.push(Array());
border_radii[0].push('0 0 30% 0');
border_radii[0].push('0 0 0 30%');
border_radii[1].push('0 30% 0 0');
border_radii[1].push('30% 0 0 0');

paddings = Array();
paddings.push(Array());
paddings.push(Array());
paddings[0].push('0 40px 40px 0');
paddings[0].push('0 0 40px 40px');
paddings[1].push('40px 40px 0 0');
paddings[1].push('40px 0 0 40px');

expand_panel = {
    'width': '75%',
    'background-color': color4,
    'color': 'white',
};

shrink_panel = {
    'width': '25%',
    'background-color': color1,
    'color': 'black',
    'border-radius': '0% 0% 0% 0%',
};

other_panel = {
    'width': '50%',
    'background-color': color1,
    'color': 'black',
    'border-radius': '0% 0% 0% 0%',
}

expand_interior = { 'background-color': color3 };

default_interior = { 'background-color': color1 }

default_text = { 'font-size': '75px',
                 'background-color': color1,
                 'color': 'black'  };

expand_text = { 'font-size': '200px',
                'background-color': color3,
                'color': 'white' };

const ur_ani = gsap.timeline();

function adjust_rows(r) {
    gsap.to(rows[r], expand_row);
    gsap.to(rows[+ !r], shrink_row);
}

let body_set = false;

function adjust_panels(r, c) {
    if(!body_set) {
        gsap.to(body, {'background-color':color1});
        body_set = true;
    }

    gsap.to(panels[r][c], expand_panel);
    gsap.to(panels[r][+ !c], shrink_panel);
    gsap.to(panels[+ !r][0], other_panel);
    gsap.to(panels[+ !r][1], other_panel);


    gsap.to(panels[r][c], {'border-radius': border_radii[r][c]});
    gsap.to(panels[r][c], {'padding': paddings[r][c]});
}

function adjust_interiors(r, c) {
    gsap.to(interiors[r][c], expand_interior);
    gsap.to(interiors[r][+ !c], default_interior);
    gsap.to(interiors[+ !r][0], default_interior);
    gsap.to(interiors[+ !r][1], default_interior);

    gsap.to(interiors[r][c], {'border-radius': border_radii[r][c]});
}

function adjust_text(r, c) {
    gsap.to(buttons[r][c], expand_text);
    gsap.to(buttons[r][+ !c], default_text);
    gsap.to(buttons[+ !r][0], default_text);
    gsap.to(buttons[+ !r][1], default_text);
}

function entering(r, c) {
    adjust_rows(r);
    adjust_panels(r, c);
    adjust_interiors(r, c);
    adjust_text(r,c);
}

ul_bttn.onclick = function () { location.href = 'solar'; };
ur_bttn.onclick = function () { location.href = 'wind'; };
bl_bttn.onclick = function () { location.href = 'insights'; };
br_bttn.onclick = function () { location.href = 'contact'; };