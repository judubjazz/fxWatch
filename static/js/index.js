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

//https://stackoverflow.com/questions/25092981/drag-drop-images-input-file-and-preview-before-upload
handleImage = (e) => {
    let reader = new FileReader();
    reader.onload = function (event) {
        $('.uploader img').attr('src',event.target.result);
    };
    reader.readAsDataURL(e.target.files[0]);
};
//---------------------------------------------------------

//https://www.w3schools.com/howto/howto_js_trigger_button_enter.asp
$(document).ready(function () {

    //TODO this has not to be always executed
    //add event on img loader
    let imageLoader = document.getElementById('filePhoto');
    imageLoader.addEventListener('change', handleImage, false);
});

/**
 * get Dom values, set fetch options then fetch
 */
submit_research = () => {
    let url = "http://localhost:5000/search";
    let query = document.getElementById('input-keyword').value;
    let filter = document.getElementById('select-option').value;

    const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: query,
            filter: filter,
            page: 1
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
                $('#input-keyword').attr('placeholder', res.error).addClass('your-class');
            }
        })
};


//-------------------------------------------------------------------------
/**
 *
 * @param animal_id
 */
view_post = (animal_id) => {
    window.location = 'http://localhost:5000/animals/' + animal_id;
};

/**
 *
 * @param page_number current page number
 * @param option next or previous
 * @param nb_page total number of pages
 */
goto_page = (page_number, option, nb_page) => {
    let url = location.pathname.split('/');
    let query = url[2];
    if (option === 'next') {
        page_number = parseInt(url[3]) + 1;
        if (page_number >= nb_page) {
            page_number = nb_page - 1
        }
        window.location = 'http://localhost:5000/search/' + query + '/' + page_number;
    } else if (option === 'previous') {
        page_number = parseInt(url[3]) - 1;
        if (page_number < 1) {
            page_number = 1
        }
        window.location = 'http://localhost:5000/search/' + query + '/' + page_number;
    } else {
        window.location = 'http://localhost:5000/search/' + query + '/' + page_number;
    }

};

