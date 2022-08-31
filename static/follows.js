
let following = document.querySelector(".following")
let followers = document.querySelector(".followers")
let user_follows = document.querySelectorAll('.user_follows')
let user_following = document.querySelectorAll('.user_following')

following.addEventListener('click', () => {
    following.style.color = '#c65959'
    followers.style.color = 'white'
    user_follows.forEach((item) => {
        item.classList.remove('hide')
    })
    user_following.forEach((item) => {
        item.classList.add('hide')
    })

})

followers.addEventListener('click', () => {
    following.style.color = 'white'
    followers.style.color = '#c65959'
    user_following.forEach((item) => {
        item.classList.remove('hide')
    })
    user_follows.forEach((item) => {
        item.classList.add('hide')
    })

})
