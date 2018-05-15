send_recovery_email = () => {
    let url = 'http://localhost:5000/password_recovery';
    let user_email = document.getElementById('email').value;

    const requestOptions = {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: user_email
        })
    };

    fetch(url, requestOptions)
        .then(response => response.json())
        .catch(err => console.log("error :" + err))
        .then(response => {
            console.log(response);
            if (response.success) {
                $('#response').css('color', 'green').html(response.msg);
            }else {
                $('#response').css('color', 'red').html(response.error);
            }
        })
};

send_validation = () => {
    let url = 'http://localhost:5000/password_recovery/validate';
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    const requestOptions = {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: username,
            password: password,
        })
    };

    fetch(url, requestOptions)
        .then(response => response.json())
        .catch(err => console.log("error :" + err))
        .then(response => {
            console.log(response);
            if (response.success) {
                window.location = response.url;
            } else {
                $('#response').css('color', 'red').html(response.error);
            }
        })
};