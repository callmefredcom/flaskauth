function closeToast() {
    document.getElementById('cookie-toast').style.display = 'none';
    localStorage.setItem('cookieAcknowledged', 'true');
}

// Show the toast only if the user hasn't acknowledged it before
window.onload = function() {
    if (!localStorage.getItem('cookieAcknowledged')) {
        document.getElementById('cookie-toast').style.display = 'block';
    }
}