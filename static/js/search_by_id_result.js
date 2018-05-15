send_email = () => {
    let url = 'https://kajaja.herokuapp.com/send_email';
    let email = document.getElementById('contact_seller_email_input').value;
    let message = document.getElementById('contact_seller_message_input').value;
    let animal_id = document.getElementById('animal_id').innerHTML;

    const requestOptions = {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: email,
            message: message,
            animal_id: animal_id,
        })
    };

    fetch(url, requestOptions)
        .then(res => res.json())
        .catch(err => {
            console.log("error :" + err)
        })
        .then(res => {
            console.log(res);
            if (res.success) {
                $('#response').css('color', 'green').html(res.msg);
            }else {
                $('#response').css('color', 'red').html(res.error);
            }
        })
};