const cityInput = document.getElementById('city-input');
const stateInput = document.getElementById('state-input');
const zipInput = document.getElementById('zipcode-input');
const latInput = document.getElementById('lat-input');
const lonInput = document.getElementById('lon-input');

const areaInput = document.getElementById('area-input');
const effInput = document.getElementById('efficiency-input');
const prInput = document.getElementById('pr-input');
const capInput = document.getElementById('capacity-input');

const backBttn = document.getElementById("hd-button");
backBttn.onclick = function () { location.href = '/' }

function submitPosition() {
    const position = {
        city: cityInput.value,
        state: stateInput.value,
        zipcode: zipInput.value,
        latitude: latInput.value,
        longitude: lonInput.value
    };

    let jsonPosition = JSON.stringify(position);

    const url = "/solar/geo"
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonPosition
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}

function submitSolarPanel() {
    const solarPanel = {
        area: areaInput.value,
        efficiency: effInput.value,
        pr: prInput.value,
        capacity: capInput.value
    };

    const jsonSP = JSON.stringify(solarPanel);
    const url = "/solar/solar-panel";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonSP
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}