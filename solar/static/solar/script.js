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

    const url = "/solar/geo"
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

function submitSolarPanel() {
    const area = document.getElementById("area-input").value;
    const efficiency = document.getElementById("efficiency-input").value;
    const pr = document.getElementById("pr-input").value;
    const capacity = document.getElementById("capacity-input").value;

    const data = {
        area: area,
        efficiency: efficiency,
        pr: pr,
        capacity: capacity
    };

    const jsonData = JSON.stringify(data);
    const url = "/solar/solar-panel";

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