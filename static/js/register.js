
const passwordField = $('#password')
const passwordRepeatField = $('#password_repeat')
const submitField = $('#register_submit')
let loginAvailable = false
let passwordCorrect = false

function checkSubmit(){
    const canSubmit = loginAvailable && passwordCorrect
    submitField.prop('disabled', !canSubmit)
    if (canSubmit){
        submitField.removeClass('disabled')
    } else {
        submitField.addClass('disabled')
    }
}

function checkPassword(){
    passwordCorrect = passwordField.val() === passwordRepeatField.val()
    if (passwordCorrect){
        passwordRepeatField.addClass('is-valid')
        passwordField.addClass('is-valid')
    } else {
        passwordRepeatField.removeClass('is-valid')
        passwordField.removeClass('is-valid')
    }
    checkSubmit()
}

const loginField = $('#login')
const loginDowntext = $('#login_downtext')

function checkAvailableLogin(){
    $.ajax({
        url: '/api/login_available',
        method: 'POST',
        dataType: "json",
        contentType: 'application/json',
        data: JSON.stringify({
            'login': loginField.val()
        }),
        success: data => {
            loginAvailable = data['is_available']
            if (loginAvailable){
                loginField.addClass('is-valid')
                loginField.removeClass('is-invalid')
                loginDowntext.text('')
            } else {
                loginField.removeClass('is-valid')
                loginField.addClass('is-invalid')
                loginDowntext.text(data['error'])
            }
            checkSubmit()
        }
    })
}

passwordField.on('input', () => checkPassword())
passwordRepeatField.on('input', () => checkPassword())
loginField.on('input', () => checkAvailableLogin())

