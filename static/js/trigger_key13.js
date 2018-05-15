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

//https://www.w3schools.com/howto/howto_js_trigger_button_enter.asp
$(document).ready(function () {
    let input = document.getElementsByClassName("key13");

// Execute a function when the user releases a key on the keyboard
    input[0].addEventListener("keyup", function (event) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            // Trigger the button element with a click
            document.getElementsByName("r_key13")[0].click();
        }
    });
});
