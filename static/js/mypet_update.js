//https://www.w3schools.com/html/tryit.asp?filename=tryhtml5_draganddrop
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    let data = ev.dataTransfer.getData("text");
    ev.target.appendChild(document.getElementById(data));
}

//---------------------------------------------------------

update_ad = (base64) => {
    let url = window.location.href;
    let name = document.getElementById('name').value;
    let type = document.getElementById('type').value;
    let race = document.getElementById('race').value;
    let age = document.getElementById('age').value;
    let description = document.getElementById('description').value;
    let img_url = document.getElementById('race').value;
    const requestOptions = {
        method: 'UPDATE',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            name: name,
            type: type,
            race: race,
            age: age,
            description: description,
            img: base64,
        })
    };

    fetch(url, requestOptions)
        .then(response => response.json())
        .catch(err => {
            console.log("error :" + err)
        })
        .then(res => {
            console.log(res);
            if (res.success) {
                window.location = res.url;
            } else {
                alert(res.error);
                $('#error').css('color', 'red').html(res.error);
            }
        })
};

delete_post = () => {

    let result = confirm("Want to delete?");
    if (result) {
        let url = "https://kajaja.herokuapp.com/mypet/update";
        const requestOptions = {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
        };

        fetch(url, requestOptions)
            .then(response => response.json())
            .catch(err => {
                console.log("error :" + err)
            })
            .then(res => {
                console.log(res);
                if (res.success) {
                    $('#response').css('color', 'green').html(res.msg);
                } else {
                    $('#response').css('color', 'red').html(res.error);
                }
            })

    }

};

//https://stackoverflow.com/questions/34972072/how-to-send-image-to-server-with-http-post-in-javascript-and-store-base64-in-mon
// This function accepts three arguments, the URL of the image to be
// converted, the mime type of the Base64 image to be output, and a
// callback function that will be called with the data URL as its argument
// once processing is complete

let convertToBase64 = function (src, imagetype, callback) {

    let img = document.createElement('IMG');
    let canvas = document.createElement('CANVAS');
    let ctx = canvas.getContext('2d');
    let data = '';

    // Set the crossOrigin property of the image element to 'Anonymous',
    // allowing us to load images from other domains so long as that domain
    // has cross-origin headers properly set

    img.crossOrigin = 'Anonymous';


    // We set the source of the image tag to start loading its data. We define
    // the event listener first, so that if the image has already been loaded
    // on the page or is cached the event listener will still fire

    img.src = src;
    canvas.height = img.height;
    canvas.width = img.width;
    ctx.drawImage(img, 0, 0);
    data = canvas.toDataURL(imagetype);
    callback(data);

};


// This wrapper function will accept the name of the image, the url, and the
// image type and perform the request
let uploadImage = function () {
    let src = document.getElementById('img').src;
    let imagetype = 'image/jpeg';

    convertToBase64(src, imagetype, function (data) {
        // sendBase64ToServer(name, data);
        update_ad(data)
    });
};


//-------------------------------------------------------------------------

//https://stackoverflow.com/questions/5802580/html-input-type-file-get-the-image-before-submitting-the-form

function readURL(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader();
        reader.onload = function (e) {
            $('#img')
                .attr('src', e.target.result)
                .width(300)
                .height(200);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

//-------------------------------------------------------------------------

$(document).ready(function () {
    readURL()
});


