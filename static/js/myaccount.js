update_myaccount = (user_id) => {
    let url = "https://kajaja.herokuapp.com/myaccount/";
    let username = document.getElementById('username').value;
    let name = document.getElementById('name').value;
    let family_name = document.getElementById('family_name').value;
    let phone = document.getElementById('phone').value;
    let address = document.getElementById('address').value;
    let password = document.getElementById('password').value;

    const requestOptions = {
        method: 'UPDATE',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({
            id: user_id,
            username: username,
            name: name,
            family_name: family_name,
            phone: phone,
            address: address,
            password: password
        }),

    };

    return fetch(url, requestOptions)
        .then(response => response.json())
        .catch(err => {
            console.log("error :" + err)
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