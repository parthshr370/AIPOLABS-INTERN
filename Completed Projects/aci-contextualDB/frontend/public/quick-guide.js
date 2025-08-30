// Quick Start Guide JavaScript
document.addEventListener('DOMContentLoaded', () => {
    let currentSlide = 0;
    const totalSlides = 4;
    
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.progress-dot');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    
    function showSlide(slideIndex) {
        // Update slides
        slides.forEach((slide, index) => {
            slide.classList.remove('active', 'prev');
            if (index === slideIndex) {
                slide.classList.add('active');
            } else if (index < slideIndex) {
                slide.classList.add('prev');
            }
        });
        
        // Update progress dots
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === slideIndex);
        });
        
        // Update navigation buttons
        prevButton.disabled = slideIndex === 0;
        
        if (slideIndex === totalSlides - 1) {
            nextButton.innerHTML = 'Start Using! <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5,3 19,12 5,21"/></svg>';
        } else {
            nextButton.innerHTML = 'Next <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>';
        }
    }
    
    function goToSlide(slideIndex) {
        if (slideIndex >= 0 && slideIndex < totalSlides) {
            currentSlide = slideIndex;
            showSlide(currentSlide);
        }
    }
    
    function goBack() {
        // Check if we have a stored original tab URL
        chrome.storage.local.get(['originalTabUrl']).then(result => {
            if (result.originalTabUrl && !result.originalTabUrl.includes('chrome-extension://')) {
                // Go to the original tab URL
                window.location.href = result.originalTabUrl;
                // Clear the stored URL
                chrome.storage.local.remove(['originalTabUrl']);
            } else {
                // Fallback: try to close the tab
                window.close();
            }
        }).catch(() => {
            // If chrome.storage is not available, try to close
            window.close();
        });
    }
    
    // Navigation event listeners
    prevButton.addEventListener('click', () => {
        if (currentSlide > 0) {
            goToSlide(currentSlide - 1);
        }
    });
    
    nextButton.addEventListener('click', () => {
        if (currentSlide < totalSlides - 1) {
            goToSlide(currentSlide + 1);
        } else {
            // Last slide - go back to original page
            goBack();
        }
    });
    
    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            goToSlide(index);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' && currentSlide > 0) {
            goToSlide(currentSlide - 1);
        } else if (e.key === 'ArrowRight' && currentSlide < totalSlides - 1) {
            goToSlide(currentSlide + 1);
        } else if (e.key === 'Enter' && currentSlide === totalSlides - 1) {
            goBack();
        }
    });
    
    // Initialize
    showSlide(0);
    console.log('Quick guide initialized');
});