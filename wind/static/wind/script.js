let csrftoken = '{{ csrf_token }}';

const back_button = document.getElementById("hd-button");
back_button.onclick = function () { location.href = '/' }

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
    let json_data = JSON.stringify(data);

    const url = "/wind/geo"
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: json_data
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}

function submitWindTurbine() {
    const efficiency_value = document.getElementById("efficiency-input").value;
    const radius_value = document.getElementById("radius-input").value;
    const height_value = document.getElementById("height-input").value;

    const data = {
        efficiency: efficiency_value,
        radius: radius_value,
        height: height_value
    };

    const json_data = JSON.stringify(data);
    const url = "/wind/wind-turbine";

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: json_data
    }).then(response => {
        if(response.ok) {
            window.location.reload();
        }
    });
}