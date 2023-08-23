const cityInput = document.getElementById('city-input');
const stateInput = document.getElementById('state-input');
const zipInput = document.getElementById('zipcode-input');
const latInput = document.getElementById('lat-input');
const lonInput = document.getElementById('lon-input');

const effInput = document.getElementById("efficiency-input");
const radInput = document.getElementById("radius-input");
const heightInput = document.getElementById("height-input");

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

    const url = "/wind/geo"
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

function submitWindTurbine() {
    const data = {
        efficiency: effInput.value,
        radius: radInput.value,
        height: heightInput.value
    };

    const jsonData = JSON.stringify(data);
    const url = "/wind/wind-turbine";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonData
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}