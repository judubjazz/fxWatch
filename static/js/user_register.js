const GLOBAL_URL = 'http://127.0.0.1:5000/';

register = () => {
    const url = GLOBAL_URL + 'register';
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        }),

    };

    return fetch(url, requestOptions)
        .then(response => response.json())
        .catch(err => {
            console.log("error :" + err);
        })
        .then(res => {
            console.log(res);
            if (res.success){
                window.location = res.url;
            }else{
                $('#error').html(res.error);

            }

        })
};

password_check = () => {
    let password = $('#password').val();
    let retype = $('#retype').val();
    if (password === retype) {
        //TODO change password check div location
        $('#error').css('color', 'green').html('good');
    } else {
        $('#error').css('color', 'red').html('X');
    }
};