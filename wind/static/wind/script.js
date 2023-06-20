const backBttn = document.getElementById("hd-button");
backBttn.onclick = function () { location.href = '/' }

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(submitPosition);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function submitPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    let data = {
        latitude: latitude,
        longitude: longitude
    };
    let jsonData = JSON.stringify(data);

    const url = "/wind/geo"
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonData
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}

function submitWindTurbine() {
    const efficiency = document.getElementById("efficiency-input").value;
    const radius = document.getElementById("radius-input").value;
    const height = document.getElementById("height-input").value;

    const data = {
        efficiency: efficiency,
        radius: radius,
        height: height
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