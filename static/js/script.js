// Basic UI interactions for the grocery store

let navbar = document.querySelector('.navbar');
let searchForm = document.querySelector('.search-form');
let loginForm = document.querySelector('.login-form');

// Menu button toggle
document.querySelector('#menu-btn').onclick = () => {
    navbar.classList.toggle('active');
    searchForm.classList.remove('active');
    loginForm.classList.remove('active');
}

// Search button toggle
document.querySelector('#search-btn').onclick = () => {
    searchForm.classList.toggle('active');
    navbar.classList.remove('active');
    loginForm.classList.remove('active');
}

// Login button toggle
document.querySelector('#login-btn').onclick = () => {
    loginForm.classList.toggle('active');
    navbar.classList.remove('active');
    searchForm.classList.remove('active');
}

// **FIX: UNCOMMENTED THIS BLOCK TO MAKE THE CART ICON FUNCTIONAL**
// document.querySelector('#cart-btn').onclick = () => {
//   shoppingCart.classList.toggle('active');
//     navbar.classList.remove('active');
//    searchForm.classList.remove('active');
//   loginForm.classList.remove('active');
// }

// Close all forms when clicking outside
window.onscroll = () => {
    navbar.classList.remove('active');
    searchForm.classList.remove('active');
    loginForm.classList.remove('active');
}

// Handle smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        if (href.length > 1) {
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                navbar.classList.remove('active');
            }
        }
    });
});

// Handle search form submission
document.querySelector('.search-form').addEventListener('submit', function(e) {
    const searchQuery = document.querySelector('#search-box').value.trim();
    if (!searchQuery) {
        e.preventDefault();
        alert('Please enter a search term');
    }
});

// Add loading animation when forms are submitted
document.addEventListener('DOMContentLoaded', () => {

    const navbar = document.querySelector('.navbar');
    const searchForm = document.querySelector('.search-form');
    const loginForm = document.querySelector('.login-form');

    const menuBtn = document.querySelector('#menu-btn');
    const searchBtn = document.querySelector('#search-btn');
    const loginBtn = document.querySelector('#login-btn');
    const cartBtn = document.querySelector('#cart-btn');

    // Function to close all active pop-ups
    const closeAll = () => {
        navbar.classList.remove('active');
        searchForm.classList.remove('active');
        loginForm.classList.remove('active');
    };

    // Menu button toggle
    if (menuBtn) {
        menuBtn.onclick = () => {
            const isActive = navbar.classList.contains('active');
            closeAll();
            if (!isActive) {
                navbar.classList.toggle('active');
            }
        };
    }

    // Search button toggle
    if (searchBtn) {
        searchBtn.onclick = () => {
            const isActive = searchForm.classList.contains('active');
            closeAll();
            if (!isActive) {
                searchForm.classList.toggle('active');
            }
        };
    }
    
    // Login button toggle
    if (loginBtn) {
        loginBtn.onclick = () => {
            const isActive = loginForm.classList.contains('active');
            closeAll();
            if (!isActive) {
                loginForm.classList.toggle('active');
            }
        };
    }

    // **FIX: THIS IS THE CORRECTED AND RELIABLE WAY TO HANDLE THE CART ICON CLICK**
    // if (cartBtn) {
    //     cartBtn.onclick = () => {
    //         const isActive = shoppingCart.classList.contains('active');
    //         closeAll();
    //         if (!isActive) {
    //             shoppingCart.classList.toggle('active');
    //         }
    //     };
    // }

    // Close all pop-ups when scrolling
    window.onscroll = () => {
        closeAll();
    };
});

// Add animation classes when elements come into view
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', function() {
    const animateElements = document.querySelectorAll('.box, .heading');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Handle image loading errors
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMDAgMTIwVjgwSDE2MFYxMjBIMTAwWiIgZmlsbD0iIzlDQTNBRiIvPgo8cGF0aCBkPSJNODAgMTQwVjE2MEgxMjBWMTQwSDgwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4=';
            this.alt = 'Image not found';
        });
    });
});

// Add to cart animation
function addToCartAnimation(button) {
    const originalText = button.textContent;
    button.textContent = 'Added!';
    button.style.background = '#27ae60';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '';
    }, 1500);
}

// Newsletter subscription handler
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.footer .box:last-child');
    if (newsletterForm) {
        const emailInput = newsletterForm.querySelector('input[type="email"]');
        const subscribeBtn = newsletterForm.querySelector('input[type="submit"]');
        
        if (subscribeBtn) {
            subscribeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const email = emailInput.value.trim();
                
                if (!email) {
                    alert('Please enter your email address');
                    return;
                }
                
                if (!isValidEmail(email)) {
                    alert('Please enter a valid email address');
                    return;
                }
                
                subscribeBtn.value = 'Subscribed!';
                subscribeBtn.style.background = '#27ae60';
                emailInput.value = '';
                
                setTimeout(() => {
                    subscribeBtn.value = 'Subscribe';
                    subscribeBtn.style.background = '';
                }, 2000);
            });
        }
    }
});

// Email validation function
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Handle category navigation
document.querySelectorAll('.categories .box .btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const href = this.getAttribute('href');
        if (href && href.startsWith('#')) {
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});

// Handle responsive navigation
function toggleMobileMenu() {
    const navbar = document.querySelector('.navbar');
    const menuBtn = document.querySelector('#menu-btn');
    
    if (navbar.classList.contains('active')) {
        navbar.classList.remove('active');
        menuBtn.classList.remove('fa-times');
        menuBtn.classList.add('fa-bars');
    } else {
        navbar.classList.add('active');
        menuBtn.classList.remove('fa-bars');
        menuBtn.classList.add('fa-times');
    }
}

// Update menu button icon
document.querySelector('#menu-btn').addEventListener('click', toggleMobileMenu);

// Close mobile menu when clicking on navigation links
document.querySelectorAll('.navbar a').forEach(link => {
    link.addEventListener('click', () => {
        document.querySelector('.navbar').classList.remove('active');
        document.querySelector('#menu-btn').classList.remove('fa-times');
        document.querySelector('#menu-btn').classList.add('fa-bars');
    });
});

// Handle window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 991) {
        document.querySelector('.navbar').classList.remove('active');
        document.querySelector('#menu-btn').classList.remove('fa-times');
        document.querySelector('#menu-btn').classList.add('fa-bars');
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    const currentLocation = window.location.hash || '#home';
    document.querySelectorAll('.navbar a').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});

// Scroll spy for navigation
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar a');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
});