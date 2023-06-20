const ds_intro_panel = document.getElementById("datasets-intro-panel");
const ds_select_panel = document.getElementById("datasets-select-panel");
const ds_info_panel = document.getElementById("datasets-info-panel");

const md_intro_panel = document.getElementById("models-intro-panel");
const md_select_panel = document.getElementById("models-select-panel");
const md_info_panel = document.getElementById("models-info-panel");

let data;
fetch('../static/insights/data.json')
    .then((response) => response.json())
    .then((json) => data = json);

function toggle_back_button(timeline, t_hide, t_show) {
    timeline.to('#back-button', {x:'100%', opacity:'0'}, t_hide);
    timeline.to('#back-button', {x:'0', opacity: '100%'}, t_show);
}

let ds_int = '#datasets-intro-panel';
let ds_sel = '#datasets-select-panel';
let ds_inf = '#datasets-info-panel';

let md_int = '#models-intro-panel';
let md_sel = '#models-select-panel';
let md_inf = '#models-info-panel';

function panel_header(side) {
    let inactiveColor = '#395754';

    if(side === 'models') {
        md_info_header = md_info_panel.querySelector('.panel-header');
        md_info_header.style.backgroundColor = inactiveColor;

        md_info_header_button = md_info_header.querySelector('button');
        md_info_header_button.style.backgroundColor = inactiveColor;
    } else {
        ds_info_header = ds_info_panel.querySelector('.panel-header');
        ds_info_header.style.backgroundColor = inactiveColor;

        ds_info_header_button = ds_info_header.querySelector('button');
        ds_info_header_button.style.backgroundColor = inactiveColor;
    }
}

function hide_panels(tm, side) {
    if(side === 'models') {
        // Selection Panel
        tm.to(ds_sel, {x:'+=50%'}, 0);
        tm.to(ds_sel, {y:'+=100%'}, 0.5);

        tm.set(ds_sel, {x: '-=50%'}, 1);
        tm.set(ds_sel, {y: '-=100%'}, 1);
        tm.set(ds_sel, {display: 'none'}, 1);

        // Info Panel
        tm.to(ds_inf, {x:'-=50%'}, 0);
        tm.to(ds_inf, {y:'+=100%'}, 0.5);

        tm.set(ds_inf, {x: '+=50%'}, 1);
        tm.set(ds_inf, {y: '-=100%'}, 1);
        tm.set(ds_inf, {display: 'none'}, 1);
    } else {
        // Selection Panel
        tm.to(md_sel, {x:'-=50%'}, 0);
        tm.to(md_sel, {y:'+=100%'}, 0.5);

        tm.set(md_sel, {x: '+=50%'}, 1);
        tm.set(md_sel, {y: '-=100%'}, 1);
        tm.set(md_sel, {display: 'none'}, 1);

        // Info Panel
        tm.to(md_inf, {x:'+=50%'}, 0);
        tm.to(md_inf, {y:'+=100%'}, 0.5);

        tm.set(md_inf, {x: '-=50%'}, 1);
        tm.set(md_inf, {y: '-=100%'}, 1);
        tm.set(md_inf, {display: 'none'}, 1);
    }
}

function show_panels(tm, side) {
    if(side == 'models') {
        tm.set(md_sel, {display:'block'}, 1.5);
        tm.from(md_sel, {x:'-=200%'}, 1.5);

        tm.set(md_inf, {display:'block'}, 1.5);
        tm.from(md_inf, {x:'+=200%'}, 1.5);
    } else {
        tm.set(ds_sel, {display:'block'}, 1.5);
        tm.from(ds_sel, {x:'+=200%'}, 1.5);

        tm.set(ds_inf, {display:'block'}, 1.5);
        tm.from(ds_inf, {x:'-=200%'}, 1.5);
    }
}


function introClicked(side) {
    let tm = gsap.timeline();

    panel_header(side);
    toggle_back_button(tm, 0, 2);

    // Hide main panels
    tm.to(ds_int, {x:'-=100%'}, 0);
    tm.to(md_int, {x:'+=110%'}, 0);
    tm.set('.intro-panel', {display:'none'}, 1);

    if(side == "datasets") {
        tm.set(ds_sel, {display:'block'}, 1);
        tm.from(ds_sel, {y: "-100%"}, 1);

        tm.set(ds_inf, {display:'block'}, 1);
        tm.from(ds_inf, {y: "100%"}, 1);
    } else {
        tm.set(md_sel, {display:'block'}, 1);
        tm.from(md_sel, {y: "-100%"}, 1);

        tm.set(md_inf, {display:'block'}, 1);
        tm.from(md_inf, {y: "100%"}, 1);
    }

    tm.play()
}


 function panelHeaderClicked(side) {
    let tm = gsap.timeline()
    toggle_back_button(tm, 0, 2);

    hide_panels(tm, side);
    show_panels(tm, side);
    panel_header(side);
    tm.play();
 }

function datasetItemSelect(item) {
    const dataset = data.datasets.find(obj => obj.name == item);

    const header = ds_info_panel.querySelector('.info-header > p');
    const content = ds_info_panel.querySelector('.info-content > p');

    header.textContent = dataset.name;
    content.textContent = dataset.description;
}

function modelItemSelect(item) {
    const dataset = data.models.find(obj => obj.name == item);

    const header = md_info_panel.querySelector('.info-header > p');
    const content = md_info_panel.querySelector('.info-content > p');
    const cont_bttn = md_info_panel.querySelector('.info-button > button');

    header.textContent = dataset.name;
    content.textContent = dataset.description;

    cont_bttn.onclick = function () { location.href = dataset.link; }
}

const back_button = document.getElementById('back-button').querySelector('button');
back_button.onclick = function () { location.href = '/'; };