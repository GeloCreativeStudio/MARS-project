/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/* Menu show */
if(navToggle){
    navToggle.addEventListener('click', () =>{
        navMenu.classList.add('show-menu')
    })
}

/* Menu hidden */
if(navClose){
    navClose.addEventListener('click', () =>{
        navMenu.classList.remove('show-menu')
    })
}


/*=============== REMOVE MENU MOBILE ===============*/
const navLink = document.querySelectorAll('.nav__link')

const linkAction = () =>{
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))


/*=============== CHANGE BACKGROUND HEADER ===============*/
// const scrollHeader = () =>{
//     const header = document.getElementById('header')
//     // Add a class if the bottom offset is greater than 50 of the viewport
//     this.scrollY >= 50 ? header.classList.add('scroll-header') 
//                        : header.classList.remove('scroll-header')
// }
// window.addEventListener('scroll', scrollHeader)

const scrollHeader = () => {
    const header = document.getElementById('header')
    header.classList.add('scroll-header')
}

// Call the function immediately to add the class on page load
scrollHeader();


/*=============== RESEARCHER SWIPER ===============*/
let swiperResearcher = new Swiper(".researcher__container", {
    loop: true,
    spaceBetween: 24,
    slidesPerView: 'auto',
    grabcursor: true,

    pagination: {
      el: ".swiper-pagination",
      dynamicBullets: true,
    },
    breakpoints: {
        768: {
          slidesPerView: 3,
        },
        1024: {
          spaceBetween: 48,
        },
      },
  });

/*=============== MIXITUP FILTER FEATURED ===============*/


/* Link active featured */ 


/*=============== SHOW SCROLL UP ===============*/ 
function scrollUp(){
	const scrollUp = document.getElementById('scroll-up')
    // When the scroll is higher than 350 viewport height, add the show-scroll class to the a tag with the scrollup class
	this.scrollY >= 350 ? scrollUp.classList.add('show-scroll')
						: scrollUp.classList.remove('show-scroll')
}
window.addEventListener('scroll', scrollUp)

/*=============== SCROLL SECTIONS ACTIVE LINK ===============*/
const sections = document.querySelectorAll('section[id]')
    
const scrollActive = () =>{
  	const scrollDown = window.scrollY

	sections.forEach(current =>{
		const sectionHeight = current.offsetHeight,
			  sectionTop = current.offsetTop - 58,
			  sectionId = current.getAttribute('id'),
			  sectionsClass = document.querySelector('.nav__menu a[href*=' + sectionId + ']')

		if(scrollDown > sectionTop && scrollDown <= sectionTop + sectionHeight){
			sectionsClass.classList.add('active-link')
		}else{
			sectionsClass.classList.remove('active-link')
		}                                                    
	})
}
window.addEventListener('scroll', scrollActive)

/*=============== SCROLL REVEAL ANIMATION ===============*/
const sr = ScrollReveal({
    origin: 'top',
    distance: '60px',
    duration: 2500,
    delay: 400,
    // reset: true,
})

// sr.reveal('.home__title, .researcher__container, .section__title')
// sr.reveal('.home__subtitle', {delay: 500})
// sr.reveal('.home__mars', {delay: 600})
// sr.reveal('.home__img', {delay: 800})
// sr.reveal('.home__ai-data', {delay: 900, interval: 100, origin: 'bottom'})
// sr.reveal('.home__button, .home__button-description', {delay: 1000, origin: 'bottom'})
// sr.reveal('.about__group', {origin: 'left'})
// sr.reveal('.about__data', {origin: 'right'})

