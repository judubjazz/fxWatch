const GLOBAL_URL = 'http://127.0.0.1:5000/';

login = () => {
    // let url = "https://kajaja.herokuapp.com/login";
    const url = GLOBAL_URL + 'login';
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const requestOptions = {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    };

    fetch(url, requestOptions)
        .then(res => res.json())
        .catch(err => {
            console.log("error :" + err);
        })
        .then(res => {
            console.log(res);
            if (res.success) {
                window.location = res.url;
            } else {
                $('#error').html(res.error);
            }
        });
};

forgot_password = () => {
    window.location = GLOBAL_URL + 'password_recovery';
};


